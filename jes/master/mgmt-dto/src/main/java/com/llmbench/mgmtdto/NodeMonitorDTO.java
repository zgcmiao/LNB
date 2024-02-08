package com.llmbench.mgmtdto;

import java.io.Serializable;
import lombok.Data;

@Data
public class NodeMonitorDTO implements Serializable {
  private String serialNum;
  private String gpuId;
  private String gpuName;
  private Integer gpuFreeMemory;
  private Integer gpuFanSpeed;
  private Integer gpuTemperature;
  private Integer gpuUsedMemory;
  private Integer gpuTotalMemory;
  private Float gpuFreeMemoryRate;
  private Float gpuMemoryRate;
  private Float gpuPowerState;
  private Float gpuUtilRate;
  private Float gpuMemoryInfoUsedRate;
}