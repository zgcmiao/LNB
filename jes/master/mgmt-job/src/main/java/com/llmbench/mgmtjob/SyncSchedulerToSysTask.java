package com.llmbench.mgmtjob;

import com.llmbench.mgmtdao.ModelInferenceTaskInfoRepository;
import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.TaskStatusEnum;
import com.llmbench.mgmtentity.ModelInferenceTaskInfo;
import com.llmbench.mgmtservices.ITaskService;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class SyncSchedulerToSysTask {

  public static final String SYS_BACKEND_SUCCESS_REQUEST_CODE = "0";
  @Autowired
  private ITaskService taskService;

  @Autowired
  private ModelInferenceTaskInfoRepository modelInferenceTaskInfoRepository;

  private static Logger logger = Logger.getLogger(SyncSchedulerToSysTask.class);

  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron = "0 0/3 * * * ?")
  private void executeFunction() {
    logger.info("Task `SyncSchedulerToSysTask` starts");
    try {
      List<ModelInferenceTaskInfo> listNotPendingTask = modelInferenceTaskInfoRepository.findModelInferenceTaskInfoByTaskStatusNotIn(
              new ArrayList<>(Arrays.asList(TaskStatusEnum.PENDING.getAlias(), TaskStatusEnum.DONE.getAlias())));
      BaseResponse response = taskService.updateSysTask(listNotPendingTask);
    } catch (Exception ex) {
      logger.error("Task `SyncSchedulerToSysTask` failed", ex);
    }
    logger.info("Task `SyncSchedulerToSysTask` completed");
  }
}
