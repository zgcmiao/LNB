package com.llmbench.agentjob;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.TaskInfoDTO;
import com.llmbench.agentservices.ITaskService;
import java.lang.management.ManagementFactory;
import java.util.Date;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class TraceModifyModelInferenceTaskStatusJob {

  @Autowired
  private ITaskService taskService;
  @Value("${SERIAL_NUM}")
  private String serialNum;

  private static Logger logger = Logger.getLogger(PostNodeHealthJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0 */5 * * * ?")
  private void executeFunction() {
    Date start = new Date();
    logger.info("Task `TraceModifyModelInferenceTaskStatusJob` starts");
    TaskInfoDTO taskInfo = new TaskInfoDTO();
    taskInfo.setSerialNum(serialNum);
    BaseResponse response = taskService.traceModifyModelInferenceTaskStatus();
    if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
      logger.info("Task `TraceModifyModelInferenceTaskStatusJob` success");
    } else{
      logger.error(String.format("Task `TraceModifyModelInferenceTaskStatusJob` failed, %s", response.getMessage()));
    }
    Date end = new Date();
  }


  private String getCurrPid() {
    String name = ManagementFactory.getRuntimeMXBean().getName();
    return name.split("@")[0];
  }
}
