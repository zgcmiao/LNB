package com.llmbench.mgmtdto;

import lombok.Data;

@Data
public class ModelInferenceTaskDTO extends TaskInfoDTO {

  private static final long serialVersionUID = -2403400204278535641L;
  private String sysTaskId;
  private String rawCommand;
  private String command;
  private String modelName;
  private Integer modelSize;
  private String affinityScope;
  private String taintScope;
  private String taskPid;
  private String taskConfig;
  private String schedulerSerialNum;
  private Boolean enableRetry;
  private Integer taskInterval;
  private Integer retryNum;
  private String outputFilePath;
  private String result;
  private String progress;

  public ModelInferenceTaskDTO(){
    this.setSysTaskId("");
    this.setCommand("");
    this.setRawCommand("");
    this.setModelName("");
    this.setModelSize(0);
    this.setAffinityScope("");
    this.setTaskConfig("");
    this.setTaintScope("");
    this.setTaskPid("");
    this.setSchedulerSerialNum("");
    this.setOutputFilePath("");
    this.setResult("");
    this.setRetryNum(0);
    this.setEnableRetry(Boolean.FALSE);
  }
}
