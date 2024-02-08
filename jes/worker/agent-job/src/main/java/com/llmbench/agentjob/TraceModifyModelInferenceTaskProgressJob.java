package com.llmbench.agentjob;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.TaskInfoDTO;
import com.llmbench.agentservices.ITaskService;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class TraceModifyModelInferenceTaskProgressJob {

  @Autowired
  private ITaskService taskService;
  @Value("${SERIAL_NUM}")
  private String serialNum;

  private static final Logger logger = Logger.getLogger(PostNodeHealthJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0/10 * * * * ?")
  private void executeFunction() {
    logger.info("Task `TraceModifyModelInferenceTaskProgressJob` starts");
    TaskInfoDTO taskInfo = new TaskInfoDTO();
    taskInfo.setSerialNum(serialNum);
    BaseResponse response = taskService.traceModifyModelInferenceProgress();
    if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
      logger.info("Task `TraceModifyModelInferenceTaskProgressJob` success");
    } else{
      logger.error(String.format("Task `TraceModifyModelInferenceTaskProgressJob` failed, %s", response.getMessage()));
    }
  }
}
