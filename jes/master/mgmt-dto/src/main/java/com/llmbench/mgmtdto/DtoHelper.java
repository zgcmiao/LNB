package com.llmbench.mgmtdto;

import java.lang.reflect.Constructor;
import java.util.ArrayList;
import java.util.List;

public class DtoHelper {

  /**
   * Entity converted to DTO
   *
   * @param list  list data
   * @param clazz DTO
   * @param <T>   T class
   * @return list result
   * @throws Exception
   */
  public static <T> List<T> castEntity(List<Object[]> list, Class<T> clazz) throws Exception {
    List<T> returnList = new ArrayList<T>();
    Object[] co = list.get(0);
    Class[] c2 = new Class[co.length];

    for (int i = 0; i < co.length; i++) {
      c2[i] = co[i].getClass();
    }

    for (Object[] o : list) {
      Constructor<T> constructor = clazz.getConstructor(c2);
      returnList.add(constructor.newInstance(o));
    }

    return returnList;
  }
}
