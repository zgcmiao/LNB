package com.llmbench.agentjob;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.NodeMonitorDTO;
import com.llmbench.agentscript.GpuMonitorCollector;
import com.llmbench.agentservices.IMonitorService;
import java.util.List;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class PostNodeMonitorJob {

  public static final String ENABLE = "ENABLE";
  @Autowired
  private IMonitorService monitorService;

  @Value("${PYTHON_INTERPRETER}")
  private String pythonInterpreter;

  @Value("${SERIAL_NUM}")
  private String serialNum;

  @Value("${MONITOR_SCRIPT_PATH}")
  private String monitorScriptPath;

  private static Logger logger = Logger.getLogger(PostNodeMonitorJob.class);
  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0/30 * * * * ?")
  private void executeFunction() {
    logger.info("Task `PostNodeMonitorJob` starts");
    try {
      GpuMonitorCollector collector = new GpuMonitorCollector();
      BaseResponse response = collector.collectMonitor(pythonInterpreter, monitorScriptPath, ENABLE);
      if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
         List<NodeMonitorDTO> listNodeMonitor = (List<NodeMonitorDTO>) response.getData();
         listNodeMonitor.forEach(x -> {
           x.setSerialNum(serialNum);
         });
        response = monitorService.postNodeMonitor(listNodeMonitor);
        if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
          logger.info("Task `PostNodeMonitorJob` success");
        } else{
          logger.error(String.format("Task `PostNodeMonitorJob` failed, %s", response.getMessage()));
        }
      } else{
        logger.error(String.format("Task `PostNodeMonitorJob` failed, %s", response.getMessage()));
      }
    } catch (Exception ex) {
      logger.error("Task `PostNodeMonitorJob` failed", ex);
    }
  }

  public static void main(String[] args) {
  }
}
