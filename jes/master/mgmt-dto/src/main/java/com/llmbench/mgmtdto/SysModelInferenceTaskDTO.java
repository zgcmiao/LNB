package com.llmbench.mgmtdto;

public class SysModelInferenceTaskDTO {

  private String code;
  private SysModelInferenceTaskDataDTO data;
  private String message;
  public void setCode(String code) {
    this.code = code;
  }
  public String getCode() {
    return code;
  }

  public void setData(SysModelInferenceTaskDataDTO data) {
    this.data = data;
  }
  public SysModelInferenceTaskDataDTO getData() {
    return data;
  }

  public void setMessage(String message) {
    this.message = message;
  }
  public String getMessage() {
    return message;
  }
}


