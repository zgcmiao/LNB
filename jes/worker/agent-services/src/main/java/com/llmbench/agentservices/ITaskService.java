package com.llmbench.agentservices;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.ModelInferenceTaskDTO;
import com.llmbench.agentdto.TaskInfoDTO;
import java.util.List;

public interface ITaskService {

  /**
   * Submit a model inference task
   *
   * @param modelInferenceTask task info
   * @return {@link BaseResponse}
   */
  BaseResponse postTaskInformation(ModelInferenceTaskDTO modelInferenceTask);

  /**
   * Get model inference task scheduling result parameters
   *
   * @param taskInfo task info
   * @return {@link BaseResponse}
   */
  BaseResponse listModelInferenceTaskSchedulerResult(TaskInfoDTO taskInfo);


  /**
   * Synchronize model inference tasks to local
   *
   * @param listTask list inference task
   * @return {@link BaseResponse}
   */
  BaseResponse syncModelInferenceTaskResult(List<ModelInferenceTaskDTO> listTask);

  /**
   * Synchronize model inference task status to management
   *
   * @param listTask list inference task
   * @return {@link BaseResponse}
   */
  BaseResponse syncModelInferenceTaskInfo(List<ModelInferenceTaskDTO> listTask);

  /**
   * Ranking model inference tasks
   *
   * @return {@link BaseResponse}
   */
  BaseResponse sortModelInferenceTask();

  /**
   * Perform model inference tasks
   *
   * @return {@link BaseResponse}
   */
  BaseResponse executeModelInferenceTask();

  /**
   * Get model inference tasks
   *
   * @return {@link BaseResponse}
   */
  BaseResponse listModelInferenceTask();

  /**
   * Track model inference task state changes
   *
   * @return {@link BaseResponse}
   */
  BaseResponse traceModifyModelInferenceTaskStatus();

  /**
   * Track progress changes of model inference tasks
   *
   * @return {@link BaseResponse}
   */
  BaseResponse traceModifyModelInferenceProgress();
}
