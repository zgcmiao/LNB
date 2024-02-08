package com.llmbench.agentutils;

import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class ConvertUtils {

  public static Map<String, Object> convertObjectToMap(Object obj) throws IllegalAccessException {
    Map<String, Object> map = new HashMap<>();
    Class<?> cls = obj.getClass();
    Field[] fields = cls.getDeclaredFields();

    for (Field field : fields) {
      field.setAccessible(true);
      String keyName = field.getName();
      Object value = field.get(obj);
      Optional result = Optional.ofNullable(value);
      if (!result.isPresent()) {
        value = "";
      }

      map.put(keyName, value);
    }
    return map;
  }
}
