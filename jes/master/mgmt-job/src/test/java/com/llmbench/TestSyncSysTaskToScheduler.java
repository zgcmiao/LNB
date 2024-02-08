package com.llmbench;

import com.alibaba.fastjson.JSON;
import com.llmbench.mgmtdto.SysModelInferenceTaskDTO;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

public class TestSyncSysTaskToScheduler {

  @Test
  public void test() {
    String fakeData = "{\n"
            + "    \"code\": \"0\",\n"
            + "    \"data\": {\n"
            + "        \"count\": \"1\",\n"
            + "        \"list\": [\n"
            + "            {\n"
            + "                \"command\": \"docker run -v ~/.cache/huggingface/hub/models--huggyllama--llama-30b:/root/.cache/huggingface/hub/models--huggyllama--llama-30b -v /tmp/{sub_task_id}/output:/llm-bench/output --gpus all --name llmbench-cf374864-6843-4c96-a279-296e7021ec8f-13 -e PYTHONPATH=/llm-bench llm-bench:1.0.18 python3 run_models.py --list_model huggyllama/llama-30b --list_subject security-cf374864-6843-4c96-a279-296e7021ec8f-13 --list_shot_type zero-shot --no-dry_run\",\n"
            + "                \"created_at\": \"2023-11-27 07:22:39\",\n"
            + "                \"delete_at\": \"None\",\n"
            + "                \"model\": \"huggyllama/llama-30b\",\n"
            + "                \"model_size\": 30,\n"
            + "                \"output_file_path\": \"\",\n"
            + "                \"output_result\": \"{}\",\n"
            + "                \"progress\": \"{}\",\n"
            + "                \"serial_num\": \"\",\n"
            + "                \"start_at\": \"None\",\n"
            + "                \"status\": \"PENDING\",\n"
            + "                \"stop_at\": \"None\",\n"
            + "                \"sub_task_config\": \"{\\\"split_batches\\\": 100, \\\"list_subject\\\": [\\\"security-cf374864-6843-4c96-a279-296e7021ec8f-13\\\"], \\\"list_shot_type\\\": [\\\"zero-shot\\\"], \\\"subject_absolute_dir\\\": \\\"C:\\\\\\\\Users\\\\\\\\xuxiu\\\\\\\\git_code\\\\\\\\llm-bench\\\\\\\\data\\\\\\\\v20230719\\\\\\\\subjects\\\", \\\"data_absolute_root\\\": \\\"C:\\\\\\\\Users\\\\\\\\xuxiu\\\\\\\\git_code\\\\\\\\llm-bench\\\\\\\\data\\\\\\\\v20230719\\\", \\\"subject_absolute_file_path\\\": \\\"tmp/llm-bench-result\\\\\\\\security-cf374864-6843-4c96-a279-296e7021ec8f-13.json\\\", \\\"data_absolute_file_path\\\": \\\"tmp/llm-bench-result\\\\\\\\cf374864-6843-4c96-a279-296e7021ec8f\\\\\\\\cf374864-6843-4c96-a279-296e7021ec8f-13.json\\\", \\\"list_model\\\": [\\\"huggyllama/llama-30b\\\"]}\",\n"
            + "                \"sub_task_id\": \"156f4718-fe94-4adc-966e-150245dc5093\",\n"
            + "                \"task_id\": \"cf374864-6843-4c96-a279-296e7021ec8f\",\n"
            + "                \"updated_at\": \"2023-11-27 07:22:39\"\n"
            + "            }\n"
            + "        ],\n"
            + "        \"page_no\": 1\n"
            + "    },\n"
            + "    \"message\": \"Success\"\n"
            + "}\n";

    boolean isJson = isJSON2(fakeData);
    SysModelInferenceTaskDTO task = JSON.parseObject(fakeData, SysModelInferenceTaskDTO.class);
    assert task != null;
//    JSONObject jsonObject = JSON.parseObject(fakeData);
//    assert jsonObject != null;
  }

  public static boolean isJSON2(String str) {
    boolean result = false;
    try {
      Object obj=JSON.parse(str);
      result = true;
    } catch (Exception e) {
      result=false;
    }
    return result;
  }

  @Test
  public void testListAdd() {
    List<String> ls = new ArrayList<>();
    ls.add("1");
    ls.add("2");
    ls.add("3");
    ls.add(1, "4");
    for (String s : ls) {
      System.out.println(s);
    }
  }
}
