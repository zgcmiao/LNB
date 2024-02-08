package com.llmbench.agentapi.apis;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.ModelInferenceTaskDTO;
import com.llmbench.agentdto.TaskInfoDTO;
import com.llmbench.agentservices.ITaskService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
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
   * @param taskInfo Get model inference task scheduling result parameters
   * @return {@link BaseResponse}
   */
  @GetMapping("/model/inference/schedulerResult")
  public BaseResponse listModelInferenceTaskSchedulerResult(TaskInfoDTO taskInfo) {
    return this.taskService.listModelInferenceTaskSchedulerResult(taskInfo);
  }
}
