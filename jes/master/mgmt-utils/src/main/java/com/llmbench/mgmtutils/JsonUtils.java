package com.llmbench.mgmtutils;

import com.alibaba.fastjson.JSONObject;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import org.apache.commons.lang3.BooleanUtils;

public class JsonUtils {
  public static String toString(Object obj){
    return JSONObject.toJSONString(obj);
  }

  /**
   * Read json file and return json string
   *
   * @param fileName
   * @return
   */
  public static String fileToJson(String fileName) throws IOException{
    String jsonStr = "";
    File jsonFile = new File(fileName);
    if (BooleanUtils.isFalse(jsonFile.exists())) {
        throw new IOException("monitor file is not existed.");
    }
    FileReader fileReader = new FileReader(jsonFile);

    Reader reader = new InputStreamReader(new FileInputStream(jsonFile), "utf-8");
    int ch = 0;
    StringBuffer sb = new StringBuffer();
    while ((ch = reader.read()) != -1) {
      sb.append((char) ch);
    }

    fileReader.close();
    reader.close();
    jsonStr = sb.toString();
    return jsonStr;
  }
}
