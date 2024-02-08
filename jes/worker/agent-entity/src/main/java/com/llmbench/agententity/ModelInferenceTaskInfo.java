package com.llmbench.agententity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Table;
import org.hibernate.annotations.Type;

@Entity
@Table(name = "T_MODEL_INFERENCE_TASK")
public class ModelInferenceTaskInfo extends BaseEntity {

  @Column(name = "serialNum", columnDefinition = "VARCHAR(64) DEFAULT ''")
  public String serialNum;

  @Column(name = "sysTaskId", columnDefinition = "VARCHAR(64) DEFAULT ''")
  public String sysTaskId;

  @Column(name = "taskId", columnDefinition = "VARCHAR(64) DEFAULT ''")
  public String taskId;
  @Column(name = "taskStatus", columnDefinition = "VARCHAR(20) DEFAULT ''")
  public String taskStatus;

  @Column(name = "command", columnDefinition = "VARCHAR(5000) DEFAULT ''")
  public String command;

  @Column(name = "modelName", columnDefinition = "VARCHAR(100) DEFAULT ''")
  public String modelName;

  @Column(name = "modelSize", columnDefinition = "TINYINT(4) DEFAULT ''")
  public Integer modelSize;

  @Column(name = "affinityScope", columnDefinition = "VARCHAR(255) DEFAULT ''")
  public String affinityScope;

  @Column(name = "taintScope", columnDefinition = "VARCHAR(255) DEFAULT ''")
  public String taintScope;

  @Column(name = "schedulerSerialNum", columnDefinition = "VARCHAR(30) DEFAULT ''")
  public String schedulerSerialNum;

  @Column(name = "taskConfig", columnDefinition = "VARCHAR(1000) DEFAULT ''")
  public String taskConfig;

  @Column(name = "priority", columnDefinition = "TINYINT(4) DEFAULT ''")
  public Integer priority;
  @Column(name = "taskPid", columnDefinition = "VARCHAR(20) DEFAULT ''")
  public String taskPid;

  @Type(type = "numeric_boolean")
  @Column(columnDefinition = "TINYINT")
  private Boolean enableRetry = false;

  @Column(name = "retryNum", columnDefinition = "TINYINT(4) DEFAULT 0")
  public Integer retryNum;

  @Column(name = "outputFilePath", columnDefinition = "VARCHAR(500) DEFAULT ''")
  public String outputFilePath;

  @Column(name = "result", columnDefinition = "VARCHAR(2000) DEFAULT ''")
  public String result;

  @Column(name = "taskInterval", columnDefinition = "TINYINT(4) DEFAULT 0")
  public Integer taskInterval;

  @Column(name = "progress", columnDefinition = "VARCHAR(30) DEFAULT ''")
  public String progress;

  public String getSysTaskId() {
    return sysTaskId;
  }

  public void setSysTaskId(String sysTaskId) {
    this.sysTaskId = sysTaskId;
  }

  public String getSerialNum() {
    return serialNum;
  }

  public void setSerialNum(String serialNum) {
    this.serialNum = serialNum;
  }

  public String getTaskId() {
    return taskId;
  }

  public void setTaskId(String taskId) {
    this.taskId = taskId;
  }

  public String getTaskStatus() {
    return taskStatus;
  }

  public void setTaskStatus(String taskStatus) {
    this.taskStatus = taskStatus;
  }

  public String getCommand() {
    return command;
  }

  public void setCommand(String command) {
    this.command = command;
  }

  public String getModelName() {
    return modelName;
  }

  public void setModelName(String modelName) {
    this.modelName = modelName;
  }

  public Integer getModelSize() {
    return modelSize;
  }

  public void setModelSize(Integer modelSize) {
    this.modelSize = modelSize;
  }

  public String getAffinityScope() {
    return affinityScope;
  }

  public void setAffinityScope(String affinityScope) {
    this.affinityScope = affinityScope;
  }

  public String getTaintScope() {
    return taintScope;
  }

  public void setTaintScope(String taintScope) {
    this.taintScope = taintScope;
  }

  public String getSchedulerSerialNum() {
    return schedulerSerialNum;
  }

  public void setSchedulerSerialNum(String schedulerSerialNum) {
    this.schedulerSerialNum = schedulerSerialNum;
  }

  public String getTaskConfig() {
    return taskConfig;
  }

  public void setTaskConfig(String taskConfig) {
    this.taskConfig = taskConfig;
  }

  public Integer getPriority() {
    return priority;
  }

  public void setPriority(Integer priority) {
    this.priority = priority;
  }

  public String getTaskPid() {
    return taskPid;
  }

  public void setTaskPid(String taskPid) {
    this.taskPid = taskPid;
  }

  public Boolean getEnableRetry() {
    return enableRetry;
  }

  public void setEnableRetry(Boolean enableRetry) {
    this.enableRetry = enableRetry;
  }

  public Integer getRetryNum() {
    return retryNum;
  }

  public void setRetryNum(Integer retryNum) {
    this.retryNum = retryNum;
  }

  public String getOutputFilePath() {
    return outputFilePath;
  }

  public void setOutputFilePath(String outputFilePath) {
    this.outputFilePath = outputFilePath;
  }

  public String getResult() {
    return result;
  }

  public void setResult(String result) {
    this.result = result;
  }

  public Integer getTaskInterval() {
    return taskInterval;
  }

  public void setTaskInterval(Integer taskInterval) {
    this.taskInterval = taskInterval;

  };

  public String getProgress() {
    return progress;
  }

  public void setProgress(String progress) {
    this.progress = progress;
  }

  public ModelInferenceTaskInfo(){
    this.setSerialNum("");
    this.setTaskId("");
    this.setTaskStatus("");
    this.setCommand("");
    this.setModelName("");
    this.setModelSize(0);
    this.setAffinityScope("");
    this.setTaintScope("");
    this.setSchedulerSerialNum("");
    this.setPriority(0);
    this.setTaskPid("");
    this.setEnableRetry(Boolean.FALSE);
    this.setRetryNum(0);
    this.setOutputFilePath("");
    this.setResult("");
  }
}