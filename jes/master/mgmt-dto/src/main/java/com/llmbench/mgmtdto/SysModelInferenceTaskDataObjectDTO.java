package com.llmbench.mgmtdto;

public class SysModelInferenceTaskDataObjectDTO {

  private String command;

  private String created_at;
  private String delete_at;
  private String model;
  private int model_size;
  private String output_file_path;
  private String output_result;
  private String progress;
  private String serial_num;
  private String start_at;
  private String status;
  private String stop_at;
  private String sub_task_config;
  private String sub_task_id;
  private String task_id;

  public String getCreated_at() {
    return created_at;
  }

  public void setCreated_at(String created_at) {
    this.created_at = created_at;
  }

  public String getUpdated_at() {
    return updated_at;
  }

  public void setUpdated_at(String updated_at) {
    this.updated_at = updated_at;
  }

  private String updated_at;

  public void setCommand(String command) {
    this.command = command;
  }

  public String getCommand() {
    return command;
  }


  public void setDelete_at(String delete_at) {
    this.delete_at = delete_at;
  }

  public String getDelete_at() {
    return delete_at;
  }

  public void setModel(String model) {
    this.model = model;
  }

  public String getModel() {
    return model;
  }

  public void setModel_size(int model_size) {
    this.model_size = model_size;
  }

  public int getModel_size() {
    return model_size;
  }

  public void setOutput_file_path(String output_file_path) {
    this.output_file_path = output_file_path;
  }

  public String getOutput_file_path() {
    return output_file_path;
  }

  public void setOutput_result(String output_result) {
    this.output_result = output_result;
  }

  public String getOutput_result() {
    return output_result;
  }

  public void setProgress(String progress) {
    this.progress = progress;
  }

  public String getProgress() {
    return progress;
  }

  public void setSerial_num(String serial_num) {
    this.serial_num = serial_num;
  }

  public String getSerial_num() {
    return serial_num;
  }

  public void setStart_at(String start_at) {
    this.start_at = start_at;
  }

  public String getStart_at() {
    return start_at;
  }

  public void setStatus(String status) {
    this.status = status;
  }

  public String getStatus() {
    return status;
  }

  public void setStop_at(String stop_at) {
    this.stop_at = stop_at;
  }

  public String getStop_at() {
    return stop_at;
  }

  public void setSub_task_config(String sub_task_config) {
    this.sub_task_config = sub_task_config;
  }

  public String getSub_task_config() {
    return sub_task_config;
  }

  public void setSub_task_id(String sub_task_id) {
    this.sub_task_id = sub_task_id;
  }

  public String getSub_task_id() {
    return sub_task_id;
  }

  public void setTask_id(String task_id) {
    this.task_id = task_id;
  }

  public String getTask_id() {
    return task_id;
  }
}
