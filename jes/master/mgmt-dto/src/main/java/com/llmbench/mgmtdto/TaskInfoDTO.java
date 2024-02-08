package com.llmbench.mgmtdto;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@Data
public class TaskInfoDTO implements Serializable {

  private static final long serialVersionUID = -2403400204278535641L;
  private String serialNum;
  private String taskId;
  private Integer priority;
  private String taskStatus;

  private Date createdTime;
  private Date updatedTime;
  private Date deletedTime;
  private Boolean deleted;
  private Date lastExecutedFinishTime;

  public TaskInfoDTO(){
    this.setTaskId("");
    this.setPriority(0);
    this.setTaskStatus("");
    this.setDeleted(Boolean.FALSE);
  }
}
