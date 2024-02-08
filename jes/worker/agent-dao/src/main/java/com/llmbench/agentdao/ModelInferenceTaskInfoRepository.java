package com.llmbench.agentdao;

import com.llmbench.agententity.ModelInferenceTaskInfo;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ModelInferenceTaskInfoRepository extends JpaRepository<ModelInferenceTaskInfo, Integer> {
  /**
   * Get tasks by TaskId
   *
   * @param taskId unique identifier of the task (assigned by the server)
   * @return {@link ModelInferenceTaskInfo}
  */
  ModelInferenceTaskInfo findModelInferenceTaskInfoByTaskId(String taskId);

  /**
   * Get tasks through task status
   *
   * @param taskStatus task status
   * @return {@link ModelInferenceTaskInfo}
   */
  List<ModelInferenceTaskInfo> findModelInferenceTaskInfoByTaskStatus(String taskStatus);

  /**
   * Get task by not equal to task status
   *
   * @param taskStatus task status
   * @return {@link ModelInferenceTaskInfo}
   */
  List<ModelInferenceTaskInfo> findModelInferenceTaskInfoByTaskStatusNot(String taskStatus);
}
