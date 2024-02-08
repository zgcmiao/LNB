package com.llmbench.mgmtentity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name = "T_NODE_MONITOR")
public class NodeMonitor extends BaseEntity {

  public String getSerialNum() {
    return serialNum;
  }

  public void setSerialNum(String serialNum) {
    this.serialNum = serialNum;
  }

  public String getGpuId() {
    return gpuId;
  }

  public void setGpuId(String gpuId) {
    this.gpuId = gpuId;
  }

  public String getGpuName() {
    return gpuName;
  }

  public void setGpuName(String gpuName) {
    this.gpuName = gpuName;
  }

  public Integer getGpuFreeMemory() {
    return gpuFreeMemory;
  }

  public void setGpuFreeMemory(Integer gpuFreeMemory) {
    this.gpuFreeMemory = gpuFreeMemory;
  }

  public Integer getGpuFanSpeed() {
    return gpuFanSpeed;
  }

  public void setGpuFanSpeed(Integer gpuFanSpeed) {
    this.gpuFanSpeed = gpuFanSpeed;
  }

  public Integer getGpuTemperature() {
    return gpuTemperature;
  }

  public void setGpuTemperature(Integer gpuTemperature) {
    this.gpuTemperature = gpuTemperature;
  }

  public Integer getGpuTotalMemory() {
    return gpuTotalMemory;
  }

  public void setGpuTotalMemory(Integer gpuTotalMemory) {
    this.gpuTotalMemory = gpuTotalMemory;
  }

  public Integer getGpuUsedMemory() {
    return gpuUsedMemory;
  }

  public void setGpuUsedMemory(Integer gpuUsedMemory) {
    this.gpuUsedMemory = gpuUsedMemory;
  }

  public String getGpuFreeMemoryRate() {
    return gpuFreeMemoryRate;
  }

  public void setGpuFreeMemoryRate(String gpuFreeMemoryRate) {
    this.gpuFreeMemoryRate = gpuFreeMemoryRate;
  }

  public String getGpuMemoryRate() {
    return gpuMemoryRate;
  }

  public void setGpuMemoryRate(String gpuMemoryRate) {
    this.gpuMemoryRate = gpuMemoryRate;
  }

  public String getGpuPowerState() {
    return gpuPowerState;
  }

  public void setGpuPowerState(String gpuPowerState) {
    this.gpuPowerState = gpuPowerState;
  }

  public String getGpuUtilRate() {
    return gpuUtilRate;
  }

  public void setGpuUtilRate(String gpuUtilRate) {
    this.gpuUtilRate = gpuUtilRate;
  }

  public String getGpuMemoryInfoUsedRate() {
    return gpuMemoryInfoUsedRate;
  }

  public void setGpuMemoryInfoUsedRate(String gpuMemoryInfoUsedRate) {
    this.gpuMemoryInfoUsedRate = gpuMemoryInfoUsedRate;
  }

  @Column(name = "serialNum")
  private String serialNum;
  @Column(name = "gpuId")
  private String gpuId;
  @Column(name = "gpuName")
  private String gpuName;
  @Column(name = "gpuFreeMemory")
  private Integer gpuFreeMemory;
  @Column(name = "gpuFanSpeed")
  private Integer gpuFanSpeed;
  @Column(name = "gpuTemperature")
  private Integer gpuTemperature;
  @Column(name = "gpuTotalMemory")
  private Integer gpuTotalMemory;
  @Column(name = "gpuUsedMemory")
  private Integer gpuUsedMemory;
  @Column(name = "gpuFreeMemoryRate")
  private String gpuFreeMemoryRate;
  @Column(name = "gpuMemoryRate")
  private String gpuMemoryRate;
  @Column(name = "gpuPowerState")
  private String gpuPowerState;
  @Column(name = "gpuUtilRate")
  private String gpuUtilRate;
  @Column(name = "gpuMemoryInfoUsedRate")
  private String gpuMemoryInfoUsedRate;
}