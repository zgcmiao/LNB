package com.llmbench.agentjob;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.ModelInferenceTaskDTO;
import com.llmbench.agentdto.TaskInfoDTO;
import com.llmbench.agentservices.ITaskService;
import java.util.List;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class SyncModelInferenceTaskInfoJob {

  @Autowired
  private ITaskService taskService;
  @Value("${SERIAL_NUM}")
  private String serialNum;
  private static Logger logger = Logger.getLogger(PostNodeHealthJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0/30 * * * * ?")
  private void executeFunction() {
    logger.info("Task `SyncModelInferenceTaskInfoJob` starts");
    try {
      TaskInfoDTO taskInfo = new TaskInfoDTO();
      taskInfo.setSerialNum(serialNum);
      BaseResponse response = taskService.listModelInferenceTask();
      if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
          response = taskService.syncModelInferenceTaskInfo((List<ModelInferenceTaskDTO>)response.getData());
        if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
          logger.info("Task `SyncModelInferenceTaskInfoJob` success");
        } else {
          logger.error(String.format("Task `SyncModelInferenceTaskInfoJob` failed, %s", response.getMessage()));
        }
      } else{
        logger.error(String.format("Task `SyncModelInferenceTaskInfoJob` failed, %s", response.getMessage()));
      }
    } catch (Exception e) {
      logger.error("Task `SyncModelInferenceTaskInfoJob` failed", e);
    }
  }
}
