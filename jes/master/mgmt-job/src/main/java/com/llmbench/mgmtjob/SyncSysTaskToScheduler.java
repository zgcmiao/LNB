package com.llmbench.mgmtjob;

import static com.llmbench.mgmtservices.TaskServiceHelper.generateTaskInterval;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.llmbench.mgmtdao.ModelInferenceTaskInfoRepository;
import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.ModelInferenceTaskDTO;
import com.llmbench.mgmtdto.SysModelInferenceTaskDTO;
import com.llmbench.mgmtdto.SysModelInferenceTaskDataObjectDTO;
import com.llmbench.mgmtdto.TaskStatusEnum;
import com.llmbench.mgmtdto.convert.SysModelInferenceTaskDTOConverter;
import com.llmbench.mgmtentity.ModelInferenceTaskInfo;
import com.llmbench.mgmtservices.ITaskService;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class SyncSysTaskToScheduler {

  public static final String SYS_BACKEND_SUCCESS_REQUEST_CODE = "0";
  public static final String LLM_BENCH_SUBJECT_FORMAT = "/llm-bench/data/metadata/%s";
  public static final String LLM_BENCH_DATA_FORMAT = "/llm-bench/data/%s";
  public static final String REPLACEMENT_TAG_SUB_TASK_ID = "{sub_task_id}";
  @Autowired
  private ITaskService taskService;

  @Autowired
  private ModelInferenceTaskInfoRepository modelInferenceTaskInfoRepository;

  private static Logger logger = Logger.getLogger(SyncSysTaskToScheduler.class);

  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0 0/2 * * * ?")
  private void executeFunction() {
    logger.info("Task `SyncSysTaskToScheduler` starts");
    try {
      BaseResponse response = taskService.syncSysTask();
      if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
        SysModelInferenceTaskDTO sysTaskInfo = JSON.parseObject((String) response.getData(),
                SysModelInferenceTaskDTO.class);
        if (SYS_BACKEND_SUCCESS_REQUEST_CODE.equals(sysTaskInfo.getCode())) {
          logger.info("Successfully obtained task list from SYS_BACKEND");
          List<ModelInferenceTaskInfo> syncList = new ArrayList<>();
          List<SysModelInferenceTaskDataObjectDTO> sysTaskList = sysTaskInfo.getData().getList();
          ModelInferenceTaskDTO modelInferenceTaskDTO = null;
          ModelInferenceTaskInfo modelInferenceTaskInfo = null;
          for (SysModelInferenceTaskDataObjectDTO obj : sysTaskList) {
            ModelInferenceTaskInfo existedTaskInfo =
                    modelInferenceTaskInfoRepository.findByTaskId(obj.getSub_task_id());
            if (existedTaskInfo == null) {
              modelInferenceTaskDTO = SysModelInferenceTaskDTOConverter.sysToScheduler(obj);
              modelInferenceTaskInfo = new ModelInferenceTaskInfo();
              BeanUtils.copyProperties(modelInferenceTaskDTO, modelInferenceTaskInfo);
              initInferenceTaskInfo(modelInferenceTaskInfo);
              syncList.add(modelInferenceTaskInfo);
            } else {
              //If the sys side status is DONE and the task status is not DONE, update the status
              if (obj.getStatus().equals(TaskStatusEnum.DONE.getAlias()) && !existedTaskInfo.getTaskStatus().equals(TaskStatusEnum.DONE.getAlias())) {
                existedTaskInfo.setTaskStatus(obj.getStatus());
                syncList.add(existedTaskInfo);
              }
            }
          }
          if (syncList.size() > 0) {
            List<String> asyncIds =
                    syncList.stream().map(ModelInferenceTaskInfo::getTaskId).collect(Collectors.toList());
            logger.info(String.format("TaskId that needs to be updated: %s", asyncIds));
            modelInferenceTaskInfoRepository.saveAll(syncList);
            logger.info(String.format("Task `SyncSysTaskToScheduler` succeeded, taskId %s",
                    syncList.stream().map(ModelInferenceTaskInfo::getTaskId).collect(Collectors.joining(","))));
          }
        } else {
          logger.error(String.format("Failed to get task list from SYS_BACKEND, %s", sysTaskInfo.getMessage()));
        }
      } else {
        logger.error(String.format("Task `SyncSysTaskToScheduler` failed, %s", response.getMessage()));
      }
    } catch (Exception ex) {
      logger.error("Task `SyncSysTaskToScheduler` failed", ex);
    }
    logger.info("Task `SyncSysTaskToScheduler` completed");
  }

  private void initInferenceTaskInfo(ModelInferenceTaskInfo modelInferenceTaskInfo) throws Exception {
    // Generate command based on parameter + rawCommand
    String rawCommand = modelInferenceTaskInfo.getRawCommand();
    String taskConfig = modelInferenceTaskInfo.getTaskConfig();
    String command = generateTaskCommand(modelInferenceTaskInfo.getTaskId(), modelInferenceTaskInfo.getSysTaskId(),
            rawCommand, taskConfig);
    Map<String, String> tagMap = new HashMap<String, String>(){{
      put(REPLACEMENT_TAG_SUB_TASK_ID,modelInferenceTaskInfo.getTaskId());
    }};
    command = dynamicReplacementTags(command, tagMap);
    modelInferenceTaskInfo.setCommand(command);
    // All inference tasks can be retried
    modelInferenceTaskInfo.setEnableRetry(Boolean.TRUE);
    //The interval between task executions in the generation interval is to avoid triggering multiple commands at the same time and causing OOM.
    modelInferenceTaskInfo.setTaskInterval(generateTaskInterval(modelInferenceTaskInfo.getModelSize()));
  }

  private String dynamicReplacementTags(String command, Map<String, String> tagMap) {
    for (Map.Entry<String, String> entry : tagMap.entrySet()) {
      command = command.replace(entry.getKey(), entry.getValue());
    }
    return command;
  }

  private String generateTaskCommand(String taskId, String sysTaskId, String rawCommand, String taskConfig) throws Exception {
    String command = "";
    // Parse taskConfig to obtain the mounting path of the subject and data
    JSONObject taskConfigObj = JSONObject.parseObject(taskConfig);
    String subjectAbsoluteFilePath = (String) taskConfigObj.get("subject_absolute_file_path");
    String dataAbsoluteFilePath = (String) taskConfigObj.get("data_absolute_file_path");
    if (StringUtils.isBlank(subjectAbsoluteFilePath) || StringUtils.isBlank(dataAbsoluteFilePath)) {
      String message = String.format("Task `%s` synchronization failed, subject and data paths cannot be empty.", taskId);
      logger.error(message);
      throw new Exception(message);
    }

    String subjectAbsoluteFileDir = subjectAbsoluteFilePath.substring(0, subjectAbsoluteFilePath.lastIndexOf("/"));
    String dataAbsoluteFileDir = dataAbsoluteFilePath.substring(0, dataAbsoluteFilePath.lastIndexOf("/"));
    logger.info(String.format("Task `%s` subject directory: %s, data directory:%s", taskId, subjectAbsoluteFileDir, dataAbsoluteFileDir));

    // Add the mounting path of subject and data
    String keyWord = "run --rm";
    String replaceKeyWord = "run--rm";
    int keyWordIndex = -1;
    int i = 0;

    rawCommand = rawCommand.replace(keyWord, replaceKeyWord);
    List<String> rawCommandArray = new ArrayList<>(Arrays.asList(rawCommand.split(" ")));
    for (String s : rawCommandArray) {
      if (s.equals(replaceKeyWord)) {
        keyWordIndex = i;
        break;
      }
      i += 1;
    }
    if (keyWordIndex > 0) {
      rawCommandArray.add(keyWordIndex + 1, String.format("-v %s:%s", subjectAbsoluteFileDir,
              String.format(LLM_BENCH_SUBJECT_FORMAT, "subjects")));
      rawCommandArray.add(keyWordIndex + 2, String.format("-v %s:%s/%s", dataAbsoluteFileDir,
              String.format(LLM_BENCH_DATA_FORMAT, "source"), sysTaskId));
      command = String.join(" ", rawCommandArray);
    }
    command = command.replace(replaceKeyWord, keyWord);
    logger.info(String.format("Task `%s` command:%s", taskId, command));
    return command;
  }
}
