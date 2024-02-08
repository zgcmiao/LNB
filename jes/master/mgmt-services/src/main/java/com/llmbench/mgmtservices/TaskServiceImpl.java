package com.llmbench.mgmtservices;

import com.alibaba.fastjson.JSON;
import com.llmbench.mgmtdao.ModelInferenceTaskInfoRepository;
import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.ErrorResponse;
import com.llmbench.mgmtdto.FilterDTO;
import com.llmbench.mgmtdto.ModelInferenceTaskDTO;
import com.llmbench.mgmtdto.ModifySysModelInferenceTaskDTO;
import com.llmbench.mgmtdto.NodeHealthDTO;
import com.llmbench.mgmtdto.NodeMonitorDTO;
import com.llmbench.mgmtdto.SuccessResponse;
import com.llmbench.mgmtdto.SysBaseTaskDTO;
import com.llmbench.mgmtdto.TaskInfoDTO;
import com.llmbench.mgmtentity.ModelInferenceTaskInfo;
import com.llmbench.mgmtutils.CommonUtils;
import com.llmbench.mgmtutils.HttpClientUtils;
import com.llmbench.mgmtutils.JsonUtils;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class TaskServiceImpl implements ITaskService {

  public static final int DEFAULT_PAGE_NO = 1;
  public static final int DEFAULT_COUNT = 1000;
  private static final String RESPONSE_CODE_SUCCESS = "success";
  private static final String SYS_BACKEND_SUCCESS_REQUEST_CODE = "0";
  private static Logger logger = Logger.getLogger(TaskServiceImpl.class);

  @Value("${SYS_BACKEND_ADDRESS}")
  private String sysBackendAddress;

  @Autowired
  private ModelInferenceTaskInfoRepository modelInferenceTaskInfoRepository;

  /**
   * Submit a model inference task
   *
   * @param modelInferenceTask task info
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse postTaskInformation(ModelInferenceTaskDTO modelInferenceTask) {
    ModelInferenceTaskInfo taskInfo = new ModelInferenceTaskInfo();
    String uuid = StringUtils.isNotBlank(modelInferenceTask.getTaskId()) ? modelInferenceTask.getTaskId() :
            CommonUtils.genUUID();
    String command = modelInferenceTask.getCommand();
    if (StringUtils.isBlank(modelInferenceTask.getCommand())) {
      return new ErrorResponse("ParameterError", "", "command is empty.", "");
    }
    // Replace template placeholder
    command = command.replace("{TASK_ID}", uuid);
    modelInferenceTask.setCommand(command.trim());
    modelInferenceTask.setTaskId(uuid);
    BeanUtils.copyProperties(modelInferenceTask, taskInfo);
    //All inference tasks can be retried
    taskInfo.setEnableRetry(Boolean.TRUE);
    //The interval between task executions in the generation interval is to avoid triggering multiple commands at the same time and causing OOM.
    taskInfo.setTaskInterval(TaskServiceHelper.generateTaskInterval(taskInfo.getModelSize()));
    taskInfo.setCreatedTime(new Date());
    modelInferenceTaskInfoRepository.save(taskInfo);
    String resMessage = "add task record successful.";
    return new SuccessResponse(null, resMessage, null);
  }

  /**
   * Get model inference task scheduling results
   *
   * @param taskInfo task info
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse listModelInferenceTaskSchedulerResult(TaskInfoDTO taskInfo) {
    String serialNum = taskInfo.getSerialNum();
    List<ModelInferenceTaskInfo> listModelInferenceTasks = modelInferenceTaskInfoRepository.findBySchedulerSerialNum(
            serialNum);
    String resMessage = "get the tasks to be executed on the SN node successful.";
    return new SuccessResponse(listModelInferenceTasks, resMessage, null);
  }

  /**
   * Synchronize model inference tasks from the agent
   *
   * @param listTask list task
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse syncModelInferenceTaskInfo(List<ModelInferenceTaskDTO> listTask) {
    List<ModelInferenceTaskInfo> unSyncTaskList = modelInferenceTaskInfoRepository.findAll();
    List<ModelInferenceTaskInfo> updateList = new ArrayList<>();
    listTask.forEach(x -> {
      //Find the task that needs to be synchronized by taskId
      Optional<ModelInferenceTaskInfo> result = unSyncTaskList.stream().filter(y -> y.getTaskId().equals(x.getTaskId()))
              .findFirst();
      if (result.isPresent()) {
        ModelInferenceTaskInfo unSyncTask = result.get();
        unSyncTask.setTaskStatus(x.getTaskStatus());
        unSyncTask.setTaskPid(x.getTaskPid());
        unSyncTask.setOutputFilePath(x.getOutputFilePath());
        unSyncTask.setResult(x.getResult());
        if (StringUtils.isNotBlank(x.getCommand())) {
          unSyncTask.setCommand(x.getCommand());
        }
        unSyncTask.setTaskInterval(x.getTaskInterval());
        unSyncTask.setEnableRetry(x.getEnableRetry());
        unSyncTask.setRetryNum(x.getRetryNum());
        unSyncTask.setProgress(x.getProgress());
        unSyncTask.setOutputFilePath(x.getOutputFilePath());
        unSyncTask.setResult(x.getResult());
        unSyncTask.setDeleted(x.getDeleted());
        unSyncTask.setUpdatedTime(x.getUpdatedTime());
        unSyncTask.setDeletedTime(x.getDeletedTime());
        unSyncTask.setLastExecutedFinishTime(x.getLastExecutedFinishTime());
        updateList.add(unSyncTask);
      }
    });
    modelInferenceTaskInfoRepository.saveAll(updateList);
    String resMessage = "post model inference status successful.";
    return new SuccessResponse("", resMessage, null);
  }

  /**
   * Model inference task scheduling
   *
   * @param listTask        Model inference tasks
   * @param listNode        Scheduling node information
   * @param listNodeMonitor Scheduling node monitoring information
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse modelInferenceTaskScheduler(List<ModelInferenceTaskDTO> listTask, List<NodeHealthDTO> listNode,
          List<NodeMonitorDTO> listNodeMonitor) {
    List<ModelInferenceTaskInfo> listModify = new ArrayList<>();
    listTask.forEach(x -> {
      // taskScheduler
      String serialNumber = schedulerTask(x, listNode, listNodeMonitor);
      if (StringUtils.isNotBlank(serialNumber)) {
        ModelInferenceTaskInfo taskInfo = modelInferenceTaskInfoRepository.findByTaskId(x.getTaskId());
        taskInfo.setSchedulerSerialNum(serialNumber);
        listModify.add(taskInfo);
      }
    });
    modelInferenceTaskInfoRepository.saveAll(listModify);
    return new SuccessResponse("", "model inference task scheduler success.", "");
  }


  /**
   * Get the specified task list
   *
   * @param filter filter
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse listModelInference(FilterDTO filter) {
    List<ModelInferenceTaskInfo> listTask = modelInferenceTaskInfoRepository.selectBySchedulerSerialNumIsEmpty();
    List<ModelInferenceTaskDTO> listTaskDTO = new ArrayList<>();
    listTask.forEach(x -> {
      ModelInferenceTaskDTO taskDTO = new ModelInferenceTaskDTO();
      BeanUtils.copyProperties(x, taskDTO);
      listTaskDTO.add(taskDTO);
    });
    return new SuccessResponse(listTaskDTO, "get model inference task success.", "");
  }

  /**
   * Sync new unexecuted tasks from benchmark llm-bench-sys
   *
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse syncSysTask() {
    logger.info("Synchronize SYS_BENCH data");
    BaseResponse response = HttpClientUtils.doGet(String.format("%s/api/task/sub_task/list?page_no=%d&count=%d",
            sysBackendAddress, DEFAULT_PAGE_NO, DEFAULT_COUNT));
    logger.info("Synchronization of SYS_BENCH data completed");
    return response;
  }

  /**
   * Update tasks synchronized from benchmark llm-bench-sys
   *
   * @param listTaskInfo Task list that needs to be synchronized
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse updateSysTask(List<ModelInferenceTaskInfo> listTaskInfo) {
    for (ModelInferenceTaskInfo taskInfo : listTaskInfo) {
      try {
        ModifySysModelInferenceTaskDTO modifySysModelInferenceTaskDTO = generateModifySysModelInferenceTaskDTO(
                taskInfo);
        BaseResponse response = HttpClientUtils.doPost(String.format("%s/api/task/sub_task/update", sysBackendAddress),
                modifySysModelInferenceTaskDTO);
        if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
          SysBaseTaskDTO sysBaseTaskDTO = JSON.parseObject((String) response.getData(), SysBaseTaskDTO.class);
          if (!SYS_BACKEND_SUCCESS_REQUEST_CODE.equals(sysBaseTaskDTO.getCode())) {
            logger.error(String.format("update sys task info failed, executed exception: %s",
                    sysBaseTaskDTO.getMessage()));
          }
        } else {
          logger.error(String.format("update sys task info failed, request exception: %s", response.getMessage()));
        }
      } catch (Exception e) {
        logger.error("update sys task info failed", e);
      }
    }
    return new SuccessResponse("", "update sys task info success.", "");
  }

  private ModifySysModelInferenceTaskDTO generateModifySysModelInferenceTaskDTO(ModelInferenceTaskInfo taskInfo) {
    ModifySysModelInferenceTaskDTO modifySysModelInferenceTaskDTO = new ModifySysModelInferenceTaskDTO();
    modifySysModelInferenceTaskDTO.setSub_task_id(taskInfo.getTaskId());
    modifySysModelInferenceTaskDTO.setCommand(taskInfo.getCommand());
    modifySysModelInferenceTaskDTO.setSub_task_config(taskInfo.getTaskConfig());
    modifySysModelInferenceTaskDTO.setSerial_num(taskInfo.getSchedulerSerialNum());
    modifySysModelInferenceTaskDTO.setOutput_file_path(taskInfo.getOutputFilePath());
    modifySysModelInferenceTaskDTO.setOutput_result(taskInfo.getResult());
    modifySysModelInferenceTaskDTO.setProgress(taskInfo.getProgress());
    modifySysModelInferenceTaskDTO.setStatus(taskInfo.getTaskStatus());
    SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    modifySysModelInferenceTaskDTO.setStart_at(format.format(taskInfo.getCreatedTime()));
    if (taskInfo.getLastExecutedFinishTime() != null) {
      modifySysModelInferenceTaskDTO.setStop_at(format.format(taskInfo.getLastExecutedFinishTime()));
    }
    return modifySysModelInferenceTaskDTO;
  }

  /**
   * Returns scheduling results based on task and resource conditions
   *
   * @param task            task
   * @param listNode        list node
   * @param listNodeMonitor list node monitor
   * @return schedule node SerialNumber
   */
  private String schedulerTask(ModelInferenceTaskDTO task, List<NodeHealthDTO> listNode,
          List<NodeMonitorDTO> listNodeMonitor) {
    logger.info(String.format("Start scheduling tasks, %s", JsonUtils.toString(task)));
    //Get available nodes
    List<String> listAvailableNode =
            listNode.stream().filter(x -> "health".equals(x.getStatus())).map(NodeHealthDTO::getSerialNum)
                    .collect(Collectors.toList());

    //Get task affinity node
    List<String> listAffinityNode =
            Arrays.stream(task.getAffinityScope().split(",")).filter(StringUtils::isNotBlank)
                    .collect(Collectors.toList());
    if (listAffinityNode.size() > 0) {
      // Take the intersection of available nodes and affinity nodes
      listAvailableNode = listAvailableNode.stream().filter(listAffinityNode::contains)
              .collect(Collectors.toList());
    }

    //Get task taint
    List<String> listTaintNode = Arrays.stream(task.getTaintScope().split(",")).filter(StringUtils::isNotBlank)
            .collect(Collectors.toList());
    if (listTaintNode.size() > 0) {
      //Difference set of available nodes and affinity nodes
      listAvailableNode = listAvailableNode.stream().filter(item -> !listTaintNode.contains(item))
              .collect(Collectors.toList());
    }

    String chooseSerialNumber = "";
    // 0 No resources available
    // 1 There is only one node
    // >1 Multiple available nodes, sort the nodes according to available resources through rules
    if (listAvailableNode.size() == 0) {
      logger.warn("No resources available for task");
    } else if (listAvailableNode.size() == DEFAULT_PAGE_NO) {
      logger.info(String.format("The task has been scheduled to the node `%s`.", listAvailableNode.get(0)));
      chooseSerialNumber = listAvailableNode.get(0);
    } else {
      //Get task scheduling rules
      Integer maxGpuMemory = 0;

      for (String x : listAvailableNode) {
        Integer nodeFreeGpuMemory =
                listNodeMonitor.stream().filter(y -> y.getSerialNum().equals(x)).map(NodeMonitorDTO::getGpuFreeMemory)
                        .reduce(Integer::sum).get();
        logger.info(String.format("Total GPU memory available for node `%s` is %d", x, nodeFreeGpuMemory));
        if (nodeFreeGpuMemory > maxGpuMemory) {
          maxGpuMemory = nodeFreeGpuMemory;
          chooseSerialNumber = x;
        }
      }
      logger.info(String.format("The task has been scheduled to the node `%s`.", chooseSerialNumber));
    }
    logger.info(String.format("Complete scheduled tasks, %s", JsonUtils.toString(task)));
    return chooseSerialNumber;
  }
}
