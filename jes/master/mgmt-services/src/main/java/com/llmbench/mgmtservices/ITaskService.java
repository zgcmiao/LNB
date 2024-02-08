package com.llmbench.mgmtservices;

import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.FilterDTO;
import com.llmbench.mgmtdto.ModelInferenceTaskDTO;
import com.llmbench.mgmtdto.NodeHealthDTO;
import com.llmbench.mgmtdto.NodeMonitorDTO;
import com.llmbench.mgmtdto.TaskInfoDTO;
import com.llmbench.mgmtentity.ModelInferenceTaskInfo;
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
   * Get model inference task scheduling results
   *
   * @param taskInfo task info
   * @return {@link BaseResponse}
   */
  BaseResponse listModelInferenceTaskSchedulerResult(TaskInfoDTO taskInfo);

  /**
   * Synchronize model inference tasks from the agent
   *
   * @param listTask Model inference tasks
   * @return {@link BaseResponse}
   */
  BaseResponse syncModelInferenceTaskInfo(List<ModelInferenceTaskDTO> listTask);

  /**
   * Model inference task scheduling
   *
   * @param listTask Model inference tasks
   * @param listNode Scheduling node information
   * @param listNodeMonitor Scheduling node monitoring information
   * @return {@link BaseResponse}
   */
  BaseResponse modelInferenceTaskScheduler(List<ModelInferenceTaskDTO> listTask, List<NodeHealthDTO> listNode,
          List<NodeMonitorDTO> listNodeMonitor);

  /**
   * Get the specified task list
   *
   * @param filter filter
   * @return {@link BaseResponse}
   */
  BaseResponse listModelInference(FilterDTO filter);

  /**
   * Sync new unexecuted tasks from benchmark llm-bench-sys
   *
   * @return {@link BaseResponse}
   */
  BaseResponse syncSysTask();

  /**
   * Update tasks synchronized from benchmark llm-bench-sys
   *
   * @param listTaskInfo Task list that needs to be synchronized
   * @return {@link BaseResponse}
   */
  BaseResponse updateSysTask(List<ModelInferenceTaskInfo> listTaskInfo);
}
