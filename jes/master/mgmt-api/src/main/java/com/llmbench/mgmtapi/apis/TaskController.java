package com.llmbench.mgmtapi.apis;

import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.ModelInferenceTaskDTO;
import com.llmbench.mgmtdto.TaskInfoDTO;
import com.llmbench.mgmtservices.ITaskService;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Component(value = "taskController")
@RequestMapping("/api/task")
public class TaskController {

  @Autowired
  private ITaskService taskService;

  /**
   * Submit a model inference task
   *
   * @param modelInferenceTask Model inference task parameters
   * @return {@link BaseResponse}
   */
  @PostMapping("/model/inference")
  public BaseResponse postModelInferenceTaskInfo(ModelInferenceTaskDTO modelInferenceTask) {
    return this.taskService.postTaskInformation(modelInferenceTask);
  }

  /**
   * Get model inference task scheduling results
   *
   * @param taskInfo task info
   * @return {@link BaseResponse}
   */
  @GetMapping("/model/inference/schedulerResult")
  public BaseResponse listModelInferenceTaskSchedulerResult(TaskInfoDTO taskInfo) {
    return this.taskService.listModelInferenceTaskSchedulerResult(taskInfo);
  }

  /**
   * Synchronize model inference tasks from the agent
   *
   * @param listTask Model inference task status
   * @return {@link BaseResponse}
   */
  @PostMapping("/model/inference/sync")
  public BaseResponse syncModelInferenceTaskInfo(@RequestBody List<ModelInferenceTaskDTO> listTask) {
    return this.taskService.syncModelInferenceTaskInfo(listTask);
  }
}
