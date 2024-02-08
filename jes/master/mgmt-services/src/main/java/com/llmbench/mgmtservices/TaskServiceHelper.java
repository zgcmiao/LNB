package com.llmbench.mgmtservices;

public class TaskServiceHelper {

  private static final Integer MIN = 0;
  private static final Integer MAX = 15;

  /**
   * The interval between task executions in the generation interval is to avoid triggering multiple commands at the same time and causing OOM.
   *
   * The larger the model, the later it is expected to be executed.
   * @param modelSize model size
   * @return Interval interval
   */
  public static Integer generateTaskInterval(Integer modelSize) {
    Integer taskInterval = (int)((MIN + Math.random() * (MAX - MIN + 1)) + (Math.random() * modelSize));
    return taskInterval;
  }
}
