package com.llmbench.agentjob;

import com.alibaba.fastjson.JSON;
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
public class GetTaskSchedulerResultJob {

  @Autowired
  private ITaskService taskService;

  private static Logger logger = Logger.getLogger(PostNodeHealthJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Value("${SERIAL_NUM}")
  private String serialNum;

  @Scheduled(cron="0/30 * * * * ?")
  private void executeFunction() {
    logger.info("Task `GetTaskSchedulerResultJob` starts");
    try {
      TaskInfoDTO taskInfo = new TaskInfoDTO();
      taskInfo.setSerialNum(serialNum);
      BaseResponse response = taskService.listModelInferenceTaskSchedulerResult(taskInfo);
      if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
          String jsonStr = JSON.toJSONString(response.getData());
          List<ModelInferenceTaskDTO> listTask = JSON.parseArray(jsonStr, ModelInferenceTaskDTO.class);
          response = taskService.syncModelInferenceTaskResult(listTask);
        if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
          logger.info("Task `GetTaskSchedulerResultJob` starts");
        } else {
          logger.error(String.format("Task `GetTaskSchedulerResultJob` failed, %s", response.getMessage()));
        }
      } else{
        logger.error(String.format("Task `GetTaskSchedulerResultJob` failed, %s", response.getMessage()));
      }
    } catch (Exception e) {
      logger.error("Task `GetTaskSchedulerResultJob` failed", e);
    }
  }
}
