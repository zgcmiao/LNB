package com.llmbench.agentutils;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import org.apache.log4j.Logger;

public class CommonUtils {
  public static Date getTime() {
    return new Date();
  }

  private static Logger logger = Logger.getLogger(CommonUtils.class);

  public static String getTimeStr() {
    return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(CommonUtils.getTime());
  }

  public static String genAbsolutePathByRootPath(String projectPathRoot, String subModule, String dir,
          String fileName) {
    if (null != fileName) {
      return String.format("%s/%s/%s/%s", projectPathRoot, subModule, dir, fileName);
    } else {
      return String.format("%s/%s/%s", projectPathRoot, dir);
    }
  }

  public static ArrayList<File> getListFiles(Object obj) {
    File directory = null;
    if (obj instanceof File) {
      directory = (File)obj;
    } else {
      directory = new File(obj.toString());
    }
    ArrayList<File> files = new ArrayList<>();
    if (directory.isFile()) {
      files.add(directory);
      return files;
    } else if (directory.isDirectory()){
      for (File file : directory.listFiles()) {
        files.addAll(getListFiles(file));
      }
    }
    return files;
  }
}
