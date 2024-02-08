package com.llmbench.mgmtentity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name = "T_NODE")
public class NodeInfo extends BaseEntity {

  @Column(name = "serialNum")
  public String serialNum;

  @Column(name = "status")
  public String status;

  public String getSerialNum() {
    return serialNum;
  }

  public void setSerialNum(String serialNum) {
    this.serialNum = serialNum;
  }

  public String getStatus() {
    return status;
  }

  public void setStatus(String status) {
    this.status = status;
  }

}