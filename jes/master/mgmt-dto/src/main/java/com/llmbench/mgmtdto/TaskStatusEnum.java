package com.llmbench.mgmtdto;

import java.util.Objects;

public enum TaskStatusEnum {
  PENDING("PENDING"),
  EXECUTED("EXECUTED"),
  SUCCESS("SUCCESS"),
  FAILED("FAILED"),
  INTERRUPT("INTERRUPT"),
  RUNNING("RUNNING"),
  OPERATION("OPERATION"),
  DONE("DONE");

  private final String alias;

  TaskStatusEnum(String alias) {
    this.alias = alias;
  }

  public String getAlias() {
    return alias;
  }

  public static TaskStatusEnum getEnumByAlias(String alias) {
    if (null == alias) {
      return null;
    }

    for (TaskStatusEnum v : values()) {
      if (Objects.equals(v.alias, alias)) {
        return v;
      }
    }
    return null;
  }
}
