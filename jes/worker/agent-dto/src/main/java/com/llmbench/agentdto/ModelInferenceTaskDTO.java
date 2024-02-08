package com.llmbench.agentdto;

import lombok.Data;

@Data
public class ModelInferenceTaskDTO extends TaskInfoDTO {

  private static final long serialVersionUID = -2403400204278535641L;
  private String sysTaskId;
  private String command;
  private String modelName;
  private Integer modelSize;
  private String affinityScope;
  private String taintScope;
  private String taskPid;
  private String taskConfig;
  private Boolean enableRetry;
  private Integer taskInterval;
  private Integer retryNum;
  private String outputFilePath;
  private String result;
  private String schedulerSerialNum;
  private String progress;

  public ModelInferenceTaskDTO() {
    this.setSysTaskId("");
    this.setCommand("");
    this.setModelName("");
    this.setTaskConfig("");
    this.setModelSize(0);
    this.setAffinityScope("");
    this.setTaintScope("");
    this.setTaskPid("");
    this.setSchedulerSerialNum("");
    this.setProgress("0");
  }
}
