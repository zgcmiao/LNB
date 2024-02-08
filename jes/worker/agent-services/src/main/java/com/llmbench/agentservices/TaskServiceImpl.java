package com.llmbench.agentservices;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.llmbench.agentdao.ModelInferenceTaskInfoRepository;
import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.ErrorResponse;
import com.llmbench.agentdto.ModelInferenceTaskDTO;
import com.llmbench.agentdto.NodeMonitorDTO;
import com.llmbench.agentdto.SuccessResponse;
import com.llmbench.agentdto.TaskInfoDTO;
import com.llmbench.agentdto.TaskStatusEnum;
import com.llmbench.agententity.ModelInferenceTaskInfo;
import com.llmbench.agentscript.GpuMonitorCollector;
import com.llmbench.agentscript.ShellCaller;
import com.llmbench.agentutils.CommonUtils;
import com.llmbench.agentutils.HttpClientUtils;
import com.llmbench.agentutils.JsonUtils;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.RandomAccessFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.io.input.ReversedLinesFileReader;
import org.apache.commons.lang3.BooleanUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class TaskServiceImpl implements ITaskService {

  public static final String TASK_OUTPUT_BASE_PATH_FORMAT = "%s/%s";
  public static final String OVERVIEW_RESULT_JSON_FILE = "overview_result.json";
  public static final String PIPELINE_ID_KEY = "pipeline_id";
  public static final String AUTO_RUN_MODEL_PIPELINE_STATUS_TXT = "auto_run_model_pipeline_status.txt";

  public static final String INFERENCE_RESULT = "%s.auto.%s-%s.json";
  public static final String PIPELINE_LOGGER_LOG = "pipeline_logger.log";

  public static final String SUCCESS = "success";
  public static final String FAILED = "failed";
  public static final String TASK_INFO_STATUS = "taskStatus";
  public static final String TASK_INFO_OUTPUT_FILE = "outputFile";
  public static final String TASK_INFO_OUTPUT_RESULT = "outputResult";
  private static final String TASK_INFO_ENABLE_RETRY = "enableRetry";

  private static final String PIPELINE_LOG = "pipelineLog";
  public static final int MILLI_SECOND_PRE_MINUTE = 60 * 1000;
  private static final int DEFAULT_RETRY_NUM_LIMIT = 3;
  public static final int TASK_PID_NOT_EXISTED_TIMEOUT = 3600 * 1000;
  public static final String CONFIG_LIST_SUBJECT = "list_subject";
  public static final String CONFIG_LIST_MODEL = "list_model";
  public static final String CONFIG_LIST_SHOT_TYPE = "list_shot_type";
  public static final String OVERVIEW_CONFIG_EXAM_INFO = "exam_info";
  public static final String OVERVIEW_CONFIG_TOTAL_NUM = "total_num";
  public static final String COMMAND_BREAKPOINT_FILE = " --breakpoint_file %s";
  public static final String COMMAND_BREAKPOINT_PIPELINE_ID = " --breakpoint_pipeline_id %s";
  public static final String HOST_OUTPUT_PATH = "/tmp/%s/output";
  public static final String CONTAINER_OUTPUT_PATH = "/llm-bench/output";
  @Autowired
  private ModelInferenceTaskInfoRepository modelInferenceTaskInfoRepository;

  @Value("${BACKEND_ADDRESS}")
  private String backendAddress;

  @Value("${NFS_PATH}")
  private String nfsPath;

  public static final String RESOURCE_MEMORY_KEY = "memory";

  private static Logger logger = Logger.getLogger(TaskServiceImpl.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  /**
   * Submit a model inference task
   *
   * @param modelInferenceTask task info
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse postTaskInformation(ModelInferenceTaskDTO modelInferenceTask) {
    return null;
  }

  /**
   * Get model inference task scheduling result parameters
   *
   * @param taskInfo task info
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse listModelInferenceTaskSchedulerResult(TaskInfoDTO taskInfo) {
    String serialNum = taskInfo.getSerialNum();
    BaseResponse response = HttpClientUtils.doGet(String.format("%s/api/task/model/inference"
            + "/schedulerResult"
            + "?serialNum=%s", backendAddress, serialNum));
    return response;
  }

  /**
   * Synchronize model inference tasks to local
   *
   * @param listTask list inference task
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse syncModelInferenceTaskResult(List<ModelInferenceTaskDTO> listTask) {
    ArrayList<ModelInferenceTaskInfo> listAddOrUpdateTask = new ArrayList<>();
    listTask.forEach(x-> {
      ModelInferenceTaskInfo task =
              modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskId(x.getTaskId());
      if (null == task) {
        task = new ModelInferenceTaskInfo();
        BeanUtils.copyProperties(x, task);
      } else {
        task.setSchedulerSerialNum(x.getSchedulerSerialNum());
        task.setPriority(x.getPriority());
        task.setSerialNum(x.getSerialNum());
        task.setTaskConfig(x.getTaskConfig());
        task.setTaskInterval(x.getTaskInterval());
        task.setUpdatedTime(CommonUtils.getTime());
        if (x.getTaskStatus().equals(TaskStatusEnum.DONE.getAlias())) {
          task.setTaskStatus(x.getTaskStatus());
        }
      }
      listAddOrUpdateTask.add(task);
    });
    modelInferenceTaskInfoRepository.saveAll(listAddOrUpdateTask);
    return new SuccessResponse("", "sync model inference task to local database successful.", "");
  }

  /**
   * Synchronize model inference task status to management
   *
   * @param listTask list inference task
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse syncModelInferenceTaskInfo(List<ModelInferenceTaskDTO> listTask) {
    BaseResponse response = new BaseResponse();
    if (listTask.size() > 0) {
      response = HttpClientUtils.doListPost(String.format(String.format("%s/api/task/model/inference"
              + "/sync", backendAddress)), listTask);
    } else {
      return new SuccessResponse("", "sync model inference task is empty.", "");
    }
    return response;
  }

  /**
   * Ranking model inference tasks " " -> PENDING
   *
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse sortModelInferenceTask() {
      GpuMonitorCollector collector = new GpuMonitorCollector();
      BaseResponse response = collector.getMonitorDataFromFile();
      if (RESPONSE_CODE_SUCCESS.equals(response.getResponseCode())) {
        List<NodeMonitorDTO> listMonitorData = (List<NodeMonitorDTO>)response.getData();

        Map<String, Integer> freeResourcesMap = getFreeResourceInfoMap(listMonitorData);
        defaultSortTask(freeResourcesMap);

        return new SuccessResponse("", "sort model inference task success.", "");
      } else {
        return new ErrorResponse(response.getResponseCode(), "", response.getMessage(), "");
      }
  }

  /**
   * Perform model inference tasks PENDING -> RUNNING
   *
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse executeModelInferenceTask() {
    List<ModelInferenceTaskInfo> listPendingTask =
            modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatus(TaskStatusEnum.PENDING.getAlias());
    String pendingTaskIds =
            listPendingTask.stream().map(ModelInferenceTaskInfo::getTaskId).collect(Collectors.joining(","));
    logger.info(String.format("Tasks in pending status：%s", pendingTaskIds));
    Date now = new Date();
    listPendingTask = listPendingTask.stream().filter(x -> now.after(x.getLastExecutedFinishTime() != null ?
            new Date(x.getLastExecutedFinishTime().getTime() + x.getTaskInterval() * MILLI_SECOND_PRE_MINUTE) :
            new Date(x.getCreatedTime().getTime() + x.getTaskInterval() * MILLI_SECOND_PRE_MINUTE)) && determineWhetherMeetTaskRuntimeRequirements(x)
            ).collect(Collectors.toList());
    pendingTaskIds = listPendingTask.stream().map(ModelInferenceTaskInfo::getTaskId).collect(Collectors.joining(","));
    logger.info(String.format("Filter tasks that meet time and resource requirements to run：%s", pendingTaskIds));
    BaseResponse result;
    if (listPendingTask.size() != 0) {
      try {
        // Determine whether available resources meet runtime needs
        boolean meetRuntimeRequirements = determineWhetherMeetTaskRuntimeRequirements(listPendingTask.get(0));
        if (meetRuntimeRequirements) {
          ModelInferenceTaskInfo pendingTask = listPendingTask.get(0);
          // Set task status to Executed
          pendingTask.setTaskStatus(TaskStatusEnum.RUNNING.getAlias());
          modelInferenceTaskInfoRepository.save(pendingTask);
          logger.info(String.format("Task `%s` status to %s -> %s", pendingTask.getTaskId(),
                  TaskStatusEnum.PENDING.getAlias(),
                  TaskStatusEnum.RUNNING.getAlias()));
          preHistoryRecode(pendingTask);
          String command = pendingTask.getCommand();
          if (StringUtils.isNotBlank(command)) {
            // Commands are separated by spaces
            List<String> listScriptArgs = new ArrayList<>();
            // Model inference tasks do not need to wait for command execution, they can be executed in the background.
            listScriptArgs.add("/bin/bash");
            listScriptArgs.add("-c");
            String[] scriptArgs = command.split(" ");
            String scriptStr = Arrays.stream(scriptArgs).map(String::trim).collect(Collectors.joining(" "));
            // Model inference is an asynchronous task, returns pid, and then uses pid to obtain the results.
            listScriptArgs.add(String.format("nohup %s > cmd.out 2>&1 & echo $!", scriptStr));

            ShellCaller caller = new ShellCaller();
            result = caller.doCall(listScriptArgs.toArray(new String[0]));

            //Update task results
            if (result.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
              String taskPid = (String)result.getData();
              pendingTask.setExecuteResult(taskPid);
              pendingTask.setTaskPid(taskPid);
            } else {
              pendingTask.setEnableRetry(Boolean.FALSE);
              pendingTask.setExecuteResult(result.getMessage());
              pendingTask.setTaskStatus(TaskStatusEnum.FAILED.getAlias());
            }
          } else {
            pendingTask.setEnableRetry(Boolean.FALSE);
            pendingTask.setExecuteResult("command is empty.");
            pendingTask.setTaskStatus(TaskStatusEnum.FAILED.getAlias());
          }
          modelInferenceTaskInfoRepository.save(pendingTask);
        }
      } catch (IOException | InterruptedException e) {
        return new ErrorResponse("BizError", "", e.getMessage(), "");
      }
    } else {
      logger.info("PENDING task not found.");
    }
    return new SuccessResponse("", "execute model inference task success.", "");
  }

  private void preHistoryRecode(ModelInferenceTaskInfo task) throws IOException {
    // If there is an output file, continue running at the breakpoint
    // Find overview file pipelineId
    String taskOutputBasePath = String.format(TASK_OUTPUT_BASE_PATH_FORMAT, nfsPath, task.getTaskId());
    Path overviewResultPath = Paths.get(taskOutputBasePath, "output", "model", OVERVIEW_RESULT_JSON_FILE);
    String outputBasePath = task.getOutputFilePath();
    String pipelineId = "";
    if (Files.exists(overviewResultPath)) {
      String overviewResultJson = getOverviewResultJson(overviewResultPath);
      pipelineId = getPipelineId(task.getTaskId(), overviewResultJson);
      if (StringUtils.isNotBlank(pipelineId)) {
        if (StringUtils.isNotBlank(outputBasePath)) {
          if (outputBasePath.contains(pipelineId)) {
            outputBasePath = outputBasePath.replace(String.format(HOST_OUTPUT_PATH, task.getTaskId()),
                    CONTAINER_OUTPUT_PATH);
            String subCommandBreakpointFile = String.format(COMMAND_BREAKPOINT_FILE, outputBasePath);
            String subCommandBreakpointPipelineId = String.format(COMMAND_BREAKPOINT_PIPELINE_ID, pipelineId);
            StringBuilder command = new StringBuilder(task.getCommand());
            insertCommand(command, subCommandBreakpointFile, -1);
            insertCommand(command, subCommandBreakpointPipelineId, -1);
            task.setCommand(command.toString());
          }
        }
      }
    }

    String result = task.getResult();
    String outputFilePath = task.getOutputFilePath();
    String[] resultFiles = result.split(",");
    File file = null;
    for(String resultFile : resultFiles) {
      if (!resultFile.equals(outputFilePath)) {
        file = new File(resultFile);
        file.delete();
      }
    }
    logger.info(String.format("Task `%s` history file cleared", task.getTaskId()));
  }

  /**
   * Get model inference tasks
   *
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse listModelInferenceTask() {
    List<ModelInferenceTaskInfo> listTask =
            modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatusNot(TaskStatusEnum.DONE.getAlias());
    List<ModelInferenceTaskDTO> listTaskDTO = new ArrayList<>();
    listTask.forEach(x -> {
      ModelInferenceTaskDTO taskDTO = new ModelInferenceTaskDTO();
      BeanUtils.copyProperties(x, taskDTO);
      listTaskDTO.add(taskDTO);
    });
    return new SuccessResponse(listTaskDTO, "list model inference task success.", "");
  }

  /**
   * Track model inference task state changes
   *
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse traceModifyModelInferenceTaskStatus() {
    // Get asynchronous tasks
    List<ModelInferenceTaskInfo> listRunningTask =
            modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatus(TaskStatusEnum.RUNNING.getAlias());
    String runningTaskIds =
            listRunningTask.stream().map(ModelInferenceTaskInfo::getTaskId).collect(Collectors.joining(","));
    logger.info(String.format("Tasks in execution state：%s", runningTaskIds));
    if (listRunningTask.size() > 0) {
      List<ModelInferenceTaskInfo> listModifyModelInferenceTask = new ArrayList<>();
      listRunningTask.forEach(x -> {
        logger.info(String.format("Task `%s` starts tracking model inference task status", x.getTaskId()));
        //Get whether the asynchronous task exists
        String[] scriptArgs = new String[]{"ps", "-p", x.getTaskPid()};
        ShellCaller caller = new ShellCaller();
        String pipelineId = "";
        try {
          BaseResponse result = caller.doCall(scriptArgs);
          // If it does not exist, the task is considered to have ended.
          if (!result.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
            logger.info(String.format("Task `%s` has been executed. Start to judge whether it is successful or not.", x.getTaskId()));
            String taskOutputBasePath = String.format(TASK_OUTPUT_BASE_PATH_FORMAT, nfsPath, x.getTaskId());
            // Specify results file
            ArrayList<File> outputFiles = CommonUtils.getListFiles(taskOutputBasePath);
            Path overviewResultPath = Paths.get(taskOutputBasePath, "output", "model", OVERVIEW_RESULT_JSON_FILE);
            Map<String, Object> taskInfo = new HashMap<>();
            Date lastExecutedFinishTime = x.getLastExecutedFinishTime() != null ? x.getLastExecutedFinishTime() :
                    x.getCreatedTime();

            // Determine whether the overview file exists
            if (!Files.exists(overviewResultPath)) {
              taskInfo = defaultGetTaskInfo(x.getTaskId(), "", outputFiles, lastExecutedFinishTime);
            } else {
              String overviewResultJson = getOverviewResultJson(overviewResultPath);
              pipelineId = getPipelineId(x.getTaskId(), overviewResultJson);
              logger.info(String.format("Task `%s` Overview row content: %s", x.getTaskId(), overviewResultJson));
              taskInfo = defaultGetTaskInfo(x.getTaskId(), overviewResultJson, outputFiles, lastExecutedFinishTime);
            }
            TaskStatusEnum taskStatus = (TaskStatusEnum)taskInfo.get(TASK_INFO_STATUS);
            logger.info(String.format("Task `%s` status is %s", x.getTaskId(), taskStatus.getAlias()));
            boolean modified = false;
            // Set the `result file` property of the inference task
            modified = setTaskOutputFilePath(x, pipelineId, taskInfo, modified);
            if (taskStatus != TaskStatusEnum.RUNNING) {
              modified = true;
              // Set whether to retry, task status, output file, result file, update time
              x.setEnableRetry(checkTaskEnableRetry(x.getEnableRetry(),
                      (boolean)taskInfo.getOrDefault(TASK_INFO_ENABLE_RETRY, true)));
              logger.info(String.format("Task `%s` status changes from %s -> %s", x.getTaskId(), x.getTaskStatus(), taskStatus));
              x.setTaskStatus(taskStatus.getAlias());
              x.setExecuteResult((String)taskInfo.get(PIPELINE_LOG));
              x.setResult(taskInfo.get(TASK_INFO_OUTPUT_RESULT).toString());
              x.setUpdatedTime(CommonUtils.getTime());
              x.setLastExecutedFinishTime(new Date());
            }
            if (BooleanUtils.isTrue(modified)) {
              listModifyModelInferenceTask.add(x);
            }
          }
        } catch (IOException | InterruptedException e) {
          logger.error(String.format("Task `%s` traces model inference task status abnormality", x.getTaskId()), e);
        }
        logger.info(String.format("Task `%s` completed tracking model inference task status", x.getTaskId()));
      });
      modelInferenceTaskInfoRepository.saveAll(listModifyModelInferenceTask);
    } else {
      logger.info("PENDING task not found.");
    }
    //Handle failed tasks
    List<ModelInferenceTaskInfo> listFailedTask =
            modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatus(TaskStatusEnum.FAILED.getAlias());
    String failedTaskIds =
            listFailedTask.stream().map(ModelInferenceTaskInfo::getTaskId).collect(Collectors.joining(","));
    logger.info(String.format("Task in failed state：%s", failedTaskIds));
    if (listFailedTask.size() > 0) {
      List<ModelInferenceTaskInfo> listModifyModelInferenceTask = new ArrayList<>();
      listFailedTask.forEach(x -> {
        boolean enableRetry = false;
        //Check if you can retry
        enableRetry = x.getEnableRetry();
        if (enableRetry) {
          // Check retries exceeded
          enableRetry = checkExceededRetryNum(x.getRetryNum());
          //Reset the task status
          if (enableRetry) {
            logger.info(String.format("Task `%s` configure retry", x.getTaskId()));
            logger.info(String.format("Task `%s` retries %d status from %s -> %s", x.getTaskId(), x.getRetryNum() + 1,
                    x.getTaskStatus(), TaskStatusEnum.PENDING.getAlias()));
            x.setRetryNum(x.getRetryNum() + 1);
            x.setTaskStatus(TaskStatusEnum.PENDING.getAlias());
            listModifyModelInferenceTask.add(x);
            modelInferenceTaskInfoRepository.save(x);
          }
        }
      });
//      if (!listModifyModelInferenceTask.isEmpty()) {
//        modelInferenceTaskInfoRepository.saveAll(listModifyModelInferenceTask);
//      }
    }
    return new SuccessResponse("", "modify async model inference task success.", "");
  }

  private static boolean setTaskOutputFilePath(ModelInferenceTaskInfo x, String pipelineId, Map<String, Object> taskInfo,
          boolean modified) {
    //If the value of the `Task Output File` field does not correspond to pipelineId, leave it blank.
    if (StringUtils.isNotBlank(pipelineId) &&
            StringUtils.isNotBlank(x.getOutputFilePath()) &&
            !x.getOutputFilePath().contains(pipelineId)) {
      modified = true;
      x.setOutputFilePath("");
    }
    //If the `task output file` field value is empty, assign a value to it
    if (StringUtils.isBlank(x.getOutputFilePath()) && StringUtils.isNotBlank(taskInfo.get(TASK_INFO_OUTPUT_FILE).toString())) {
      modified = true;
      x.setOutputFilePath(taskInfo.get(TASK_INFO_OUTPUT_FILE).toString());
    }
    if (BooleanUtils.isTrue(modified)) {
      logger.info(String.format("Task `%s` The task output file is %s", x.getTaskId(), x.getOutputFilePath()));
    }
    return modified;
  }

  @NotNull
  public static String getOverviewResultJson(Path overviewResultPath) throws IOException {
    String overviewResultStr = "";
    try (RandomAccessFile randomAccessFile = new RandomAccessFile(overviewResultPath.toFile().getAbsolutePath(), "r")) {
      long fileLength = randomAccessFile.length();
      StringBuilder lastLine = new StringBuilder();
      long pointer = fileLength - 1;
      //Find the first character that is not \n
      while (pointer >= 0) {
        randomAccessFile.seek(pointer);
        int currentByte = randomAccessFile.read();
        if (currentByte != '\n') {
          break;
        }
        pointer--;
      }
      // Find newline characters starting from the end of the file and looking forward
      while (pointer >= 0) {
        randomAccessFile.seek(pointer);
        int currentByte = randomAccessFile.read();
        if (currentByte == '\n') {
          break;
        }
        lastLine.insert(0, (char) currentByte);
        pointer--;
      }
      overviewResultStr = lastLine.toString();
    } catch (IOException e) {
      logger.error("Failed to read overview file.");
      throw e;
    }
    return overviewResultStr;
  }

  /**
   * Track progress changes of model inference tasks
   *
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse traceModifyModelInferenceProgress() {
    //Get asynchronous tasks
    List<ModelInferenceTaskInfo> listRunningTask =
            modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatus(TaskStatusEnum.RUNNING.getAlias());
    if (listRunningTask.size() > 0) {
      listRunningTask.forEach(x -> {
        logger.info(String.format("Task `%s` starts calculating evaluation progress", x.getTaskId()));
        try {
          String taskOutputBasePath = String.format(TASK_OUTPUT_BASE_PATH_FORMAT, nfsPath, x.getTaskId());
          //Get results file
          Path overviewResultPath = Paths.get(taskOutputBasePath, "output", "model", OVERVIEW_RESULT_JSON_FILE);
          logger.info(String.format("Task `%s` overviewResultPath %s", x.getTaskId(), overviewResultPath));
          if (overviewResultPath.toFile().exists()) {
            // Get the result file of the inference task
            Path inferenceResultPath = getInferenceTaskResultFile(x, overviewResultPath, taskOutputBasePath);
            logger.info(String.format("Task `%s` inferenceResultPath %s", x.getTaskId(), inferenceResultPath.toString()));
            long finishCount = countFileLines(inferenceResultPath);
            // Get the total number of rows
            String overviewResultJson = getOverviewResultJson(overviewResultPath);
            JSONObject overviewConfigObj = JSONArray.parseObject(overviewResultJson);
            JSONObject examInfo = (JSONObject) overviewConfigObj.get(OVERVIEW_CONFIG_EXAM_INFO);
            Integer totalNum = (Integer) examInfo.get(OVERVIEW_CONFIG_TOTAL_NUM);
            logger.info(String.format("Task `%s` Completed number of lines: %d, Total number of lines: %d", x.getTaskId(), finishCount, totalNum));
            // Set the `result file` property of the inference task
            if (StringUtils.isBlank(x.getOutputFilePath()) || !x.getOutputFilePath().equals(
                    Objects.requireNonNull(inferenceResultPath).toString())) {
              x.setOutputFilePath(String.valueOf(inferenceResultPath));
              logger.info(String.format("Task `%s` Result file of inference task: %s", x.getTaskId(), x.getOutputFilePath()));
            }
            HashMap<String, Object> result = new HashMap<>();
            result.put("count", finishCount);
            result.put("total", totalNum);
            x.setProgress(JsonUtils.toString(result));
            modelInferenceTaskInfoRepository.save(x);
          } else {
            logger.error(String.format("Task `%s` overviewResultPath is not found.", x.getTaskId()));
          }
        } catch (Exception e) {
          logger.error(String.format("Task `%s` calculation and evaluation progress abnormality", x.getTaskId()), e);
        }
      });
    }
    return new SuccessResponse("", "modify async model inference progress success.", "");
  }

  private static long countFileLines(Path filePath) throws IOException {
    Stream<String> lines = Files.lines(filePath);
    long count = lines.count();
    lines.close();
    return count;
  }

  /**
   * Get the result file of the inference task
   *
   * @param modelInferenceTaskInfo
   * @param taskOutputBasePath
   * @throws IOException
   */
  private static Path getInferenceTaskResultFile(ModelInferenceTaskInfo modelInferenceTaskInfo,
          Path overviewResultPath, String taskOutputBasePath) throws IOException {
    //Determine whether the overview file exists
    if (Files.exists(overviewResultPath)) {
      //Parse taskConfig to obtain subject, model and shotType
      JSONObject taskConfigObj = JSONObject.parseObject(modelInferenceTaskInfo.getTaskConfig());
      JSONArray listSubject = (JSONArray) taskConfigObj.get(CONFIG_LIST_SUBJECT);
      JSONArray listModel = (JSONArray) taskConfigObj.get(CONFIG_LIST_MODEL);
      JSONArray listShotType = (JSONArray) taskConfigObj.get(CONFIG_LIST_SHOT_TYPE);
      String subject = listSubject.get(0).toString();
      String model = listModel.get(0).toString().replace("/", "-");
      String shotType = listShotType.get(0).toString();
      // get pipeline id
      String overviewResultJson = getOverviewResultJson(overviewResultPath);
      logger.info(String.format("Task `%s` overview %s", modelInferenceTaskInfo.getTaskId(), overviewResultJson));
      String pipelineId = getPipelineId(modelInferenceTaskInfo.getTaskId(), overviewResultJson);
      Path inferenceResultPath = Paths.get(
              taskOutputBasePath, "output", "model", model, String.format(INFERENCE_RESULT, pipelineId, subject, shotType));
      logger.info(String.format("Task `%s` result path is %s", modelInferenceTaskInfo.getTaskId(), inferenceResultPath.toString()));
      return inferenceResultPath;
    } else {
      logger.info(String.format("Task `%s` overview file does not exist", modelInferenceTaskInfo.getTaskId()));
    }
    return null;
  }

  /**
   * Check if the number of retries has been exceeded
   *
   * @return Whether to allow retries
   */
  private boolean checkExceededRetryNum(int retryNum) {
    return retryNum < DEFAULT_RETRY_NUM_LIMIT;
  }

 /**
  * Determine whether retry is allowed from the task attribute field and execution result
  * @param fromRaw Determine whether the task is retryable from the original attributes
  * @param fromResult Determine whether it can be retried based on the execution results
  * @return Whether to allow retries
  */
  private boolean checkTaskEnableRetry(boolean fromRaw, boolean fromResult) {
    return fromRaw && fromResult;
  }

  /**
   * Default method for tracking review task status
   * Find the success/failure mark from the hanging directory of the llm-bench container. If there is none, it is considered to still be in the OPERATION state.
   *
   * @return {@link Map<String, Object>}
   */
  public Map<String, Object> defaultGetTaskInfo(String taskId, String overviewResultJson, ArrayList<File> outputFiles,
          Date lastExecutedFinishTime)
          throws IOException {
    Map<String, Object> result = new HashMap<>();
    String outputFile = "";
    String outputResult = "";
    String pipelineLog = "";
    boolean enableRetry = true;
    TaskStatusEnum status = null;

    // Get status file
    File autoRunModelPipelineStatusFile = getRunModelStatusFile(taskId, outputFiles);

    // Overview file exists
    if (StringUtils.isNotBlank(overviewResultJson)) {
      logger.info(String.format("Task `%s`, overview file exists", taskId));

      String pipelineId = getPipelineId(taskId, overviewResultJson);
      logger.info(String.format("Task `%s` <pipelineId>:%s", taskId, pipelineId));

      // Whether the result file is written and whether it needs to wait
      if (autoRunModelPipelineStatusFile != null) {
        logger.info(String.format("Task `%s` <pipelineId>:%s, result file created %s", taskId, pipelineId, autoRunModelPipelineStatusFile.getAbsolutePath()));
        status = getTaskStatus(autoRunModelPipelineStatusFile, taskId, pipelineId);
        if (status == null) {
          status = TaskStatusEnum.RUNNING;
        }
        logger.info(String.format("Task `%s` <pipelineId>:%s, the task status is %s ", taskId, pipelineId, status.getAlias()));
        // Get output files and output results
        outputFile = getOutputFile(pipelineId, outputFiles);
        outputResult = getOutputResult(outputFiles);
        logger.info(String.format("Task `%s` <pipelineId>:%s, outputFile:%s, outputResult:%s", taskId, pipelineId, outputFile, outputResult));
      } else {
        status = TaskStatusEnum.OPERATION;
        logger.error(String.format("Task `%s` <pipelineId>:%s, \n"
                + "The overview file exists, the result file is not created, and the task running status is abnormal.", taskId, pipelineId));
      }
    }
    //Overview file does not exist
    else {
      logger.info(String.format("Task `%s`, overview file does not exist", taskId));
      // Whether the result file is written and whether it needs to wait
      if (autoRunModelPipelineStatusFile != null) {
        logger.info(String.format("Task `%s`, result file created %s", taskId, autoRunModelPipelineStatusFile.getAbsolutePath()));
        //
        //Determine whether the task has failed. For example: OOM situation causes the status file not to be created, but the status has failed. In this case, the pipelineId cannot be found and can only be defaulted to the first line.
        status = getTaskStatus(autoRunModelPipelineStatusFile, taskId, "");
        if (status == null) {
          status = TaskStatusEnum.RUNNING;
        }
        // Get output files and output results
        outputFile = getOutputFile("", outputFiles);
        outputResult = getOutputResult(outputFiles);
        logger.info(String.format("Task `%s`, outputFile:%s, outputResult:%s", taskId, outputFile, outputResult));
      }
      //If the status file still does not exist after more than 12 hours, it will be set to failure directly.
      else if (new Date().after(new Date(lastExecutedFinishTime.getTime() + TASK_PID_NOT_EXISTED_TIMEOUT * 12))) {
        status = TaskStatusEnum.OPERATION;
        outputResult = getOutputResult(outputFiles);
        logger.error(String.format("Task `%s`, The result file was not created and the task running status was abnormal.", taskId));
      }
      // Task is still running
      else {
        status = TaskStatusEnum.RUNNING;
        outputResult = getOutputResult(outputFiles);
        logger.info(String.format("Task `%s` The task status is %s and the overview file is to be created.", taskId, TaskStatusEnum.RUNNING.getAlias()));
      }
    }

    result.put(TASK_INFO_STATUS, status);
    result.put(TASK_INFO_ENABLE_RETRY, enableRetry);
    result.put(TASK_INFO_OUTPUT_FILE, outputFile);
    result.put(TASK_INFO_OUTPUT_RESULT, outputResult);
    if (status.equals(TaskStatusEnum.FAILED) || status.equals(TaskStatusEnum.OPERATION)) {
      pipelineLog = getPipelineLogContent(taskId, outputFiles, 50);
    }
    result.put(PIPELINE_LOG, pipelineLog);
    return result;
  }

  private static String getPipelineId(String taskId, String overviewResultJson) throws IOException {
    // get pipeline id
    JSONObject overviewResultJsonObject = null;
    try {
      overviewResultJsonObject = JSONObject.parseObject(overviewResultJson);
    } catch (Exception e) {
      throw new IOException(String.format("Task `%s`, overview file format is incorrect", taskId));
    }
    return overviewResultJsonObject.getString(PIPELINE_ID_KEY);
  }

  @Nullable
  private File getRunModelStatusFile(String taskId, ArrayList<File> outputFiles) {
    // get auto_run_model_pipeline_status file
    File autoRunModelPipelineStatusFile = null;
    for (File file : outputFiles) {
      if (file.getName().equals(AUTO_RUN_MODEL_PIPELINE_STATUS_TXT)) {
        autoRunModelPipelineStatusFile = file;
        break;
      }
    }
    logger.info(String.format("Task `%s` <autoRunModelPipelineStatusFile>:%s", taskId,
            autoRunModelPipelineStatusFile != null ? autoRunModelPipelineStatusFile.getAbsolutePath() : ""));
    return autoRunModelPipelineStatusFile;
  }

  @Nullable
  private String getPipelineLogContent(String taskId, ArrayList<File> outputFiles, Integer tailLines)
          throws IOException {
    File pipelineLogFile = null;
    for (File file : outputFiles) {
      if (file.getName().equals(PIPELINE_LOGGER_LOG)) {
        pipelineLogFile = file;
        break;
      }
    }
    logger.info(String.format("Task `%s` <pipelineLogFile>:%s", taskId,
            pipelineLogFile != null ? pipelineLogFile.getAbsolutePath() : ""));
    if (pipelineLogFile == null){
      return "";
    }
    return getTailFile(pipelineLogFile, tailLines);
  }

  public String getTailFile(File file, Integer tailLines) throws IOException {
      int lines = tailLines;
      ReversedLinesFileReader reader = new ReversedLinesFileReader(file);
      StringBuilder builder = new StringBuilder();
      for (int i = 0; i < lines; i++) {
        String line = reader.readLine();
        if (line == null) {
          break;
        }
        builder.insert(0, line + "\n");
      }
      reader.close();
      return builder.toString();
  }

  private TaskStatusEnum getTaskStatus(File autoRunModelPipelineStatusFile, String taskId, String pipelineId)
          throws IOException {
    TaskStatusEnum status = null;
    FileInputStream inputStream = new FileInputStream(autoRunModelPipelineStatusFile.getAbsolutePath());
    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
    String str = null;
    while((str = bufferedReader.readLine()) != null)
    {
      if (StringUtils.isNotBlank(pipelineId)) {
        logger.info(String.format("Task `%s` has a pipelineId. Find the corresponding row according to the pipelineId, and then find SUCCESS/FAILED to judge.", taskId));
        logger.info(String.format("Task `%s` <autoRunModelPipelineStatusFile content>:%s", taskId, str));
        if (str.contains(pipelineId) && str.contains(SUCCESS)) {
          logger.info(String.format("Task `%s` success", taskId));
          status = TaskStatusEnum.SUCCESS;
        }
        if (str.contains(pipelineId) && str.contains(FAILED)) {
          logger.info(String.format("Task `%s` failed", taskId));
          status = TaskStatusEnum.FAILED;
        }
      }
      // Without pipelineId, determine whether the text contains SUCCESS/FAILED
      else {
        logger.info(String.format("Task `%s` has no pipelineId, find SUCCESS/FAILED to judge", taskId));
        if (str.contains(SUCCESS)) {
          status = TaskStatusEnum.SUCCESS;
        }
        if (str.contains(FAILED)) {
          status = TaskStatusEnum.FAILED;
        }
      }
    }
    inputStream.close();
    bufferedReader.close();
    return status;
  }

  private String getOutputFile(String pipelineId, ArrayList<File> outputFiles) {
    if (StringUtils.isBlank(pipelineId)) {
      return "";
    }
    return outputFiles.stream().filter(x ->
            x.getName().contains(pipelineId)
            && x.getName().contains("auto")
            && x.getName().contains("shot")
            && x.getName().contains("json")).map(File::getAbsolutePath).findFirst().orElse("");
  }

  private String getOutputResult(ArrayList<File> outputFiles) {
    return outputFiles.stream().map(Object::toString).collect(Collectors.joining(","));
  }

  /**
   * Based on monitoring data, prioritize tasks by estimating resources
   * Strategy: There is and only one task in the pending execution state
   *
   * @param freeResourcesMap free resource map
   *
   */
  private void defaultSortTask(Map<String, Integer> freeResourcesMap) {
    // Get tasks to be executed
    List<ModelInferenceTaskInfo> listPendingTask =
            modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatus(TaskStatusEnum.PENDING.getAlias());
    String pendingTaskIds =
            listPendingTask.stream().map(ModelInferenceTaskInfo::getTaskId).collect(Collectors.joining(","));
    logger.info(String.format("Tasks in pending status：%s", pendingTaskIds));
    if (listPendingTask.size() == 0) {
      //Get unsorted tasks
      List<ModelInferenceTaskInfo> listUnSortedTask =
              modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatus(new String());

      if (listUnSortedTask.size() != 0) {
        Date now = new Date();
        //Get the first task according to the rules. The current time is greater than the creation time + TaskInterval
        List<ModelInferenceTaskInfo> sortedModelInferenceTask =
                listUnSortedTask.stream()
                        .filter(x -> now.after(x.getLastExecutedFinishTime() != null ?
                                new Date(x.getLastExecutedFinishTime().getTime() + x.getTaskInterval() * MILLI_SECOND_PRE_MINUTE) :
                                new Date(x.getCreatedTime().getTime() + x.getTaskInterval() * MILLI_SECOND_PRE_MINUTE)))
                        .sorted(
                // Sort by priority, the higher the priority, the higher the priority
                Comparator.comparing(ModelInferenceTaskInfo::getPriority, Comparator.reverseOrder())
                        //In order of priority, the smaller the model size, the higher it is.
                        .thenComparing(ModelInferenceTaskInfo::getModelSize)).collect(Collectors.toList());
        if (sortedModelInferenceTask.isEmpty()) {
          logger.info("There is currently no suitable task to perform.");
          return;
        }
        Optional<ModelInferenceTaskInfo> result = sortedModelInferenceTask.stream().findFirst();
        ModelInferenceTaskInfo firstTask = result.get();
        logger.info(String.format("task: %s.", JsonUtils.toString(firstTask), firstTask.getPriority(),
                firstTask.getModelSize()));

        Map<String, Integer> estimateResourcesMap = estimateTaskResources(firstTask);

        logger.info(String.format("The minimum resource requirement is %s M, and the free resources are %s M",
                estimateResourcesMap.get(RESOURCE_MEMORY_KEY),
                freeResourcesMap.get(RESOURCE_MEMORY_KEY)));

        if (estimateResourcesMap.get(RESOURCE_MEMORY_KEY) < freeResourcesMap.get(RESOURCE_MEMORY_KEY)) {
          //Set the initial state of the selected task
          firstTask.setTaskStatus(TaskStatusEnum.PENDING.getAlias());
          firstTask.setUpdatedTime(CommonUtils.getTime());
          modelInferenceTaskInfoRepository.save(firstTask);
          logger.info(String.format("Task `%s` status changes from %s -> %s", firstTask.getTaskId(), "NULL",
                  TaskStatusEnum.PENDING.getAlias()));
          logger.info(String.format("The selected task status is set to [%s] status.", TaskStatusEnum.PENDING.getAlias()));
        } else {
          logger.warn("Insufficient resources are required for the selected task");
        }
      } else {
        logger.info("There is currently no suitable task to perform.");
      }
    } else {
      logger.warn("Selected tasks waiting to be executed.");
    }
  }

  /**
   * Estimate task resources
   *
   * @param taskInfo task info
   */
  private Map<String, Integer> estimateTaskResources(ModelInferenceTaskInfo taskInfo) {
    Map<String, Integer> estimateResourcesMap = new HashMap<>();
    Integer modelSize = taskInfo.getModelSize();
    estimateResourcesMap.put(RESOURCE_MEMORY_KEY, estimateMemory(modelSize));
    return estimateResourcesMap;
  }

  /**
   * Determine whether task operation requirements are met
   *
   * @param taskInfo  task info
   * @return Whether it meets operational requirements
   */
  private boolean determineWhetherMeetTaskRuntimeRequirements(ModelInferenceTaskInfo taskInfo) {
    boolean isMeet = false;
    logger.info(String.format("Task `%s` determines whether it meets the task running requirements", taskInfo.getTaskId()));
    GpuMonitorCollector collector = new GpuMonitorCollector();
    BaseResponse response = collector.getMonitorDataFromFile();
    if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
      List<NodeMonitorDTO> listNodeMonitor = (List<NodeMonitorDTO>) response.getData();
      int totalGpuFreeMemory = listNodeMonitor.stream().mapToInt(NodeMonitorDTO::getGpuFreeMemory).sum();
      Map<String, Integer> estimateResourcesMap = estimateTaskResources(taskInfo);
      int runtimeRequirements = estimateResourcesMap.get(RESOURCE_MEMORY_KEY);
      isMeet = totalGpuFreeMemory >= runtimeRequirements;
      if (isMeet) {
        logger.info(String.format("The resources of task `%s` meet the task running requirements, idle resources: %s M, running requirements: %s M", taskInfo.getTaskId(), totalGpuFreeMemory,
                runtimeRequirements));
        return true;
      } else {
        logger.info(String.format("The resources of task `%s` cannot meet the task running requirements, idle resources: %s M, running requirements: %s M", taskInfo.getTaskId(),
                totalGpuFreeMemory,
                runtimeRequirements));
        return false;
      }
    } else{
      logger.error(String.format("Failed to obtain monitoring data, %s", response.getMessage()));
      logger.info(String.format("Task `%s` cannot determine whether it meets the task running requirements.", taskInfo.getTaskId()));
      return false;
    }
  }

  /**
   * Estimate memory usage, estimated based on parameter size
   *
   * @param modelSize Model size
   * @return
   */
  private Integer estimateMemory(Integer modelSize) {
    if (modelSize <= 7){
      return 50 * 1000;
    } else if (modelSize <= 13) {
      return 90 * 1000;
    } else if (modelSize <= 30) {
      return 130 * 1000;
    } else if (modelSize <= 65) {
      return 160 * 1000;
    } else {
      return 48 * 4 * 1000;
    }
  }


  /**
   * Obtain the idle resource map through monitoring data
   *
   * @param listMonitorData Monitoring data
   * @return idle resources Map<String, Integer>
   */
  private static Map<String, Integer> getFreeResourceInfoMap(List<NodeMonitorDTO> listMonitorData) {
    Map<String, Integer> freeResourceInfoMap = new HashMap<>();

    Integer freeMemory = 0;
    logger.info("Resources are as follows:");
    for (NodeMonitorDTO monitor : listMonitorData) {
      freeMemory += monitor.getGpuFreeMemory();

      logger.info(String.format(">>> GPUId: %s, GPU name: %s， available video memory size: %d M", monitor.getGpuId(),
              monitor.getGpuName(),
              monitor.getGpuFreeMemory()));
    }
    logger.info(String.format(">>> Total available video memory size: %d M", freeMemory));
    freeResourceInfoMap.put("memory", freeMemory);
    return freeResourceInfoMap;
  }

  private void insertCommand(StringBuilder oldCommand, String newSubCommandStr, Integer index) {
    if (index < 0) {
      if (oldCommand.indexOf(newSubCommandStr) < 0) {
        oldCommand.append(newSubCommandStr);
      }
    }
  }
}
