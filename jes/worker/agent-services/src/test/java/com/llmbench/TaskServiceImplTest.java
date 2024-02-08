package com.llmbench;

import com.alibaba.fastjson.JSONObject;
import com.llmbench.agentservices.TaskServiceImpl;
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Objects;
import org.junit.Ignore;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.junit4.SpringRunner;

@RunWith(SpringRunner.class)
public class TaskServiceImplTest {

  private TaskServiceImpl taskService = new TaskServiceImpl();

  @Test
  public void test() throws IOException {
    String overviewResultJson = "{\"model_name\": \"huggyllama-llama-7b\", \"pipeline_id\": "
            + "\"b5e4ccee-8845-11ee-9575-ec2a723c9928\", \"exam_info\": {\"subject\": \"security-min\", \"total_num\": 1}}";
    taskService.defaultGetTaskInfo("", overviewResultJson, new ArrayList<>(), new Date());
  }

  @Test
  public void testTime() {
    Date d1 = new Date();
    Date d2 = new Date();
    SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    System.out.println(sdf.format(d1));
    d1 = new Date(d1.getTime() + 1000);
    // +1 second
    System.out.println(sdf.format(d1));

    Date d4 = new Date(d1.getTime() + 3 * 60 * 1000);
    System.out.println(sdf.format(d4));
    assert d1.after(d2);
  }
}
