package com.llmbench;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.llmbench.agentutils.JsonUtils;
import java.text.DecimalFormat;
import java.util.HashMap;
import java.util.Objects;
import org.junit.jupiter.api.Test;

/**
 * Unit test for simple App.
 */

public class AppTest
{
    @Test
    public void testGetConfigFromJson() {
        String taskConfig = "{\"split_batches\": 50000, "
                + "\"list_shot_type\": [\"five-shot\"], "
                + "\"data_absolute_root\": \"/tmp/llm-bench-sys-data/gpt_gen_mcq/mcq_0.json\", "
                + "\"llm_bench_docker_version\": \"1.0.24\", "
                + "\"llm_bench_version\": \"v20231212\", "
                + "\"subject_absolute_file_path\": \"/data1/tmp/llm-bench-result/2e9006a2-e3cd-4400-a552-df8274649de2/subjects/default-2e9006a2-e3cd-4400-a552-df8274649de2-0.json\", "
                + "\"data_absolute_file_path\": \"/data1/tmp/llm-bench-result/2e9006a2-e3cd-4400-a552-df8274649de2/source/2e9006a2-e3cd-4400-a552-df8274649de2/2e9006a2-e3cd-4400-a552-df8274649de2-0.json\", "
                + "\"list_subject\": [\"default-2e9006a2-e3cd-4400-a552-df8274649de2-0\"], "
                + "\"list_model\": [\"baichuan-inc/Baichuan-13B-Chat\"]}";
        JSONObject taskConfigObj = JSONObject.parseObject(taskConfig);
        JSONArray listSubject = (JSONArray) taskConfigObj.get("list_subject");
        JSONArray listModel = (JSONArray) taskConfigObj.get("list_model");
        JSONArray listShotType = (JSONArray) taskConfigObj.get("list_shot_type");
        String subject = listSubject.get(0).toString();
        String model = listModel.get(0).toString();
        String shotType = listShotType.get(0).toString();
        assert subject.equals("default-2e9006a2-e3cd-4400-a552-df8274649de2-0");
        assert model.equals("baichuan-inc/Baichuan-13B-Chat");
        assert shotType.equals("five-shot");

        String overviewConfig = "{\"model_name\": \"baichuan-inc-Baichuan-13B-Base\", "
                + "\"pipeline_id\": \"1b153992-a06e-11ee-80e3-0242ac110009\", "
                + "\"exam_info\": "
                + "{\"subject\": \"default-08677eb2-5c98-41c4-a770-1b3b362371c8-0\", "
                + "\"total_num\": 49955}}";
        JSONObject overviewConfigObj = JSONArray.parseObject(overviewConfig);
        JSONObject examInfo = (JSONObject) overviewConfigObj.get("exam_info");
        Integer totalNum = (Integer) examInfo.get("total_num");
        assert totalNum == 49955;

        Integer finishCount = 46185;
        Integer totalNum1 = 49955;
        DecimalFormat decimalFormat = new DecimalFormat("0.00");
        String result = decimalFormat.format((double)finishCount / totalNum1);
        assert Objects.equals(result, "0.92");

        HashMap hMap = new HashMap();
        hMap.put("count", finishCount);
        hMap.put("total", totalNum);
        String hStr = JsonUtils.toString(hMap);
        assert hStr.equals("{\"total\":49955,\"count\":46185}");
    }
}
