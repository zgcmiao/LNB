package com.llmbench.mgmtdao;

import com.llmbench.mgmtentity.ModelInferenceTaskInfo;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface ModelInferenceTaskInfoRepository extends JpaRepository<ModelInferenceTaskInfo, Integer> {

  /**
   * Search by SN number
   *
   * @param serialNum sn
   * @return {@link List<ModelInferenceTaskInfo>}
   */
  List<ModelInferenceTaskInfo> findBySchedulerSerialNum(String serialNum);

  /**
   * Query by task ID
   *
   * @param taskId task id
   * @return {@link ModelInferenceTaskInfo}
   */
  ModelInferenceTaskInfo findByTaskId(String taskId);

  /**
   * Get the list to be scheduled
   *
   * @return {@link List<ModelInferenceTaskInfo>}
   */
  @Query(value = "SELECT * FROM T_MODEL_INFERENCE_TASK m WHERE m.SCHEDULER_SERIAL_NUM = ''", nativeQuery = true)
  List<ModelInferenceTaskInfo> selectBySchedulerSerialNumIsEmpty();

  /**
   * Get the task by not equal to the specified task status
   *
   * @param listTaskStatus Task status list
   * @return {@link ModelInferenceTaskInfo}
   */
  List<ModelInferenceTaskInfo> findModelInferenceTaskInfoByTaskStatusNotIn(List<String> listTaskStatus);
}
