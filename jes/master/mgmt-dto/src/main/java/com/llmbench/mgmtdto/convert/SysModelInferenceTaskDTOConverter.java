package com.llmbench.mgmtdto.convert;

import com.llmbench.mgmtdto.ModelInferenceTaskDTO;
import com.llmbench.mgmtdto.SysModelInferenceTaskDataObjectDTO;
import java.text.ParseException;
import java.util.Date;
import org.apache.commons.lang3.time.DateUtils;

public class SysModelInferenceTaskDTOConverter {

  public static final String NONE = "None";

  public static ModelInferenceTaskDTO sysToScheduler(
          SysModelInferenceTaskDataObjectDTO sysModelInferenceTaskDataObjectDTO) throws ParseException {
    ModelInferenceTaskDTO modelInferenceTaskDTO = new ModelInferenceTaskDTO();
    modelInferenceTaskDTO.setModelName(sysModelInferenceTaskDataObjectDTO.getModel());
    modelInferenceTaskDTO.setModelSize(sysModelInferenceTaskDataObjectDTO.getModel_size());
    modelInferenceTaskDTO.setTaskId(sysModelInferenceTaskDataObjectDTO.getTask_id());
    // command -> rawCommand
    modelInferenceTaskDTO.setRawCommand(sysModelInferenceTaskDataObjectDTO.getCommand());
    modelInferenceTaskDTO.setTaskStatus(sysModelInferenceTaskDataObjectDTO.getStatus());
    modelInferenceTaskDTO.setTaskConfig(sysModelInferenceTaskDataObjectDTO.getSub_task_config());
    // subTaskId -> taskId
    modelInferenceTaskDTO.setTaskId(sysModelInferenceTaskDataObjectDTO.getSub_task_id());
    // taskId -> sysTaskId
    modelInferenceTaskDTO.setSysTaskId(sysModelInferenceTaskDataObjectDTO.getTask_id());

    if (!NONE.equals(sysModelInferenceTaskDataObjectDTO.getCreated_at())) {
      modelInferenceTaskDTO.setCreatedTime(DateUtils.parseDate(sysModelInferenceTaskDataObjectDTO.getCreated_at(),
              "yyyy-MM-dd HH:mm:ss"));
    } else {
      modelInferenceTaskDTO.setCreatedTime(new Date());
    }
    if (!NONE.equals(sysModelInferenceTaskDataObjectDTO.getUpdated_at())) {
      modelInferenceTaskDTO.setUpdatedTime(DateUtils.parseDate(sysModelInferenceTaskDataObjectDTO.getUpdated_at(),
              "yyyy-MM-dd HH:mm:ss"));
    }
    if (!NONE.equals(sysModelInferenceTaskDataObjectDTO.getDelete_at())) {
      modelInferenceTaskDTO.setDeletedTime(DateUtils.parseDate(sysModelInferenceTaskDataObjectDTO.getDelete_at(),
              "yyyy-MM-dd HH:mm:ss"));
    }
    return modelInferenceTaskDTO;
  }
}
