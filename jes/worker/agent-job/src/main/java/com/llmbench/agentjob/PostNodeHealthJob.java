package com.llmbench.agentjob;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.NodeHealthDTO;
import com.llmbench.agentservices.IMonitorService;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class PostNodeHealthJob {

  @Autowired
  private IMonitorService monitorService;

  @Value("${SERIAL_NUM}")
  private String serialNum;
  private static Logger logger = Logger.getLogger(PostNodeHealthJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";
  public static final String HEALTH_STATUS = "health";

  @Scheduled(cron="0/10 * * * * ?")
  private void executeFunction() {
    logger.info("Task `PostNodeHealthJob` starts");
    try {
      NodeHealthDTO nodeHealthDTO = getDefaultNodeHealthStatus(serialNum);
      BaseResponse response = monitorService.postNodeHealth(nodeHealthDTO);
      if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
        logger.info("Task `PostNodeHealthJob` starts");
      } else{
        logger.error(String.format("Task `PostNodeHealthJob` failed, %s", response.getMessage()));
      }
    } catch (Exception e) {
      logger.error("Task `PostNodeHealthJob` failed", e);
    }
  }

  private static NodeHealthDTO getDefaultNodeHealthStatus(String serialNum) {
    NodeHealthDTO nodeHealthDTO = new NodeHealthDTO();
    nodeHealthDTO.setSerialNum(serialNum);
    nodeHealthDTO.setStatus(HEALTH_STATUS);
    return nodeHealthDTO;
  }

  public static void main(String[] args)  {
  }
}

