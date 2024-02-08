package com.llmbench.mgmtentity;

import com.llmbench.mgmtutils.CommonUtils;
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

  public Date createdTime = CommonUtils.getTime();
  public Date updatedTime = null;

  public Date deletedTime = null;

  private Date lastExecutedFinishTime = null;

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

  public Date getCreatedTime() {
    return createdTime;
  }

  public void setCreatedTime(Date createdTime) {
    this.createdTime = createdTime;
  }

  public Date getLastExecutedFinishTime() {
    return lastExecutedFinishTime;
  }

  public void setLastExecutedFinishTime(Date lastExecutedFinishTime) {
    this.lastExecutedFinishTime = lastExecutedFinishTime;
  }

  @Type(type = "numeric_boolean")
  @Column(columnDefinition = "TINYINT")
  private Boolean deleted = false;

}
