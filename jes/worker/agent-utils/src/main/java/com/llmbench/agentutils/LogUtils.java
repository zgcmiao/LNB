package com.llmbench.agentutils;

import org.apache.log4j.Logger;

public class LogUtils {
  public static Logger logger = Logger.getLogger(LogUtils.class);

  public static void main(String[] args){
    logger.info("info log");
    logger.debug("test log");
    logger.error("error log");
  }
}
