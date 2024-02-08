package com.llmbench.agentjob;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentservices.ITaskService;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class SortModelInferenceTaskJob {

  @Autowired
  private ITaskService taskService;
  private static Logger logger = Logger.getLogger(SortModelInferenceTaskJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0/5 * * * * ?")
  private void executeFunction() {
    try {
      logger.info("Task `SortModelInferenceTaskJob` starts");

      BaseResponse response = taskService.sortModelInferenceTask();
      if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
        logger.info("Task `SortModelInferenceTaskJob` success");
      } else{
        logger.error(String.format("Task `SortModelInferenceTaskJob` failed, %s", response.getMessage()));
      }
    } catch (Exception e) {
      logger.error("Task `SortModelInferenceTaskJob` failed", e);
    }
  }

  public static void main(String[] args)  {
  }
}

