package com.llmbench.mgmtutils;

import java.util.Date;
import java.util.UUID;

public class CommonUtils {
  public static Date getTime() {
    return new Date();
  }

  public static String genUUID() {
    return UUID.randomUUID().toString().replace("-", "").toLowerCase();
  }
}
