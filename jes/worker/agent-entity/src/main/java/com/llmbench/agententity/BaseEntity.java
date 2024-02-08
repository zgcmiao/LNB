package com.llmbench.agententity;

import com.llmbench.agentutils.CommonUtils;
import java.util.Date;
import javax.persistence.Column;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.MappedSuperclass;
import org.hibernate.annotations.Type;

@MappedSuperclass
public class BaseEntity {

  @Id
  @Column(name = "id")
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  public Integer id;

  private Date createdTime = CommonUtils.getTime();
  @Column(name = "executeResult", columnDefinition = "CLOB")
  private String executeResult;
  private Date updatedTime = null;
  private Date deletedTime = null;
  private Date lastExecutedFinishTime = null;

  @Type(type = "numeric_boolean")
  @Column(columnDefinition = "TINYINT")
  private Boolean deleted = false;
  public Date getCreatedTime() {
    return createdTime;
  }

  public void setCreatedTime(Date createdTime) {
    this.createdTime = createdTime;
  }

  public Date getUpdatedTime() {
    return updatedTime;
  }

  public void setUpdatedTime(Date updatedTime) {
    this.updatedTime = updatedTime;
  }

  public Date getDeletedTime() {
    return deletedTime;
  }

  public void setDeletedTime(Date deletedTime) {
    this.deletedTime = deletedTime;
  }

  public Boolean getDeleted() {
    return deleted;
  }

  public void setDeleted(Boolean deleted) {
    this.deleted = deleted;
  }

  public String getExecuteResult() {
    return executeResult;
  }

  public void setExecuteResult(String executeResult) {
    this.executeResult = executeResult;
  }

  public Date getLastExecutedFinishTime() {
    return lastExecutedFinishTime;
  }

  public void setLastExecutedFinishTime(Date lastExecuteFinishTime) {
    this.lastExecutedFinishTime = lastExecuteFinishTime;
  }


}
