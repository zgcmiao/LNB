package com.llmbench.agentjob;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentservices.ITaskService;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
@Component
public class ExecuteModelInferenceTaskJob {

  @Autowired
  private ITaskService taskService;
  private static Logger logger = Logger.getLogger(ExecuteModelInferenceTaskJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0 0/1 * * * ?")
  private void executeFunction() {
    logger.info("Task `ExecuteModelInferenceTaskJob` starts");
    try {
      BaseResponse response = taskService.executeModelInferenceTask();
      if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
        logger.info("Task `ExecuteModelInferenceTaskJob` success");
      } else{
        logger.error(String.format("Task `ExecuteModelInferenceTaskJob` failed, %s", response.getMessage()));
      }
    } catch (Exception e) {
      logger.error("Task `ExecuteModelInferenceTaskJob` failed", e);
    }
  }

  public static void main(String[] args)  {
  }
}

