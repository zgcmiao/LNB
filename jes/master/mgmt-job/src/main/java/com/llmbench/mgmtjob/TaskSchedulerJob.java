package com.llmbench.mgmtjob;

import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.ModelInferenceTaskDTO;
import com.llmbench.mgmtdto.NodeHealthDTO;
import com.llmbench.mgmtdto.NodeMonitorDTO;
import com.llmbench.mgmtservices.IMonitorService;
import com.llmbench.mgmtservices.ITaskService;
import java.util.ArrayList;
import java.util.List;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class TaskSchedulerJob {

  @Autowired
  private ITaskService taskService;
  @Autowired
  private IMonitorService monitorService;
  private static Logger logger = Logger.getLogger(TaskSchedulerJob.class);

  public static final String RESPONSE_CODE_SUCCESS = "success";

  @Scheduled(cron="0/10 * * * * ?")
  private void executeFunction() {
    logger.info("Task `TaskSchedulerJob` starts");
    BaseResponse response;
    List<ModelInferenceTaskDTO> listTask = new ArrayList<>();
    List<NodeHealthDTO> listNode = new ArrayList<>();
    List<NodeMonitorDTO> listNodeMonitor = new ArrayList<>();

    response = taskService.listModelInference(null);
    if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
      listTask = (List<ModelInferenceTaskDTO>)response.getData();
    }
    response = monitorService.listNodeHealth(null);
    if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
      listNode = (List<NodeHealthDTO>)response.getData();
    }
    response = monitorService.listNodeMonitor(null);
    if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
      listNodeMonitor = (List<NodeMonitorDTO>)response.getData();
    }

    response = taskService.modelInferenceTaskScheduler(listTask, listNode, listNodeMonitor);
    if (response.getResponseCode().equals(RESPONSE_CODE_SUCCESS)) {
      logger.info(String.format("Task `TaskSchedulerJob` starts"));
    } else{
      logger.error(String.format("Task `TaskSchedulerJob` failed, %s", response.getMessage()));
    }
    logger.info("Task `TaskSchedulerJob` starts");
  }
}
