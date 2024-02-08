package com.llmbench.agentscript;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.ErrorResponse;
import com.llmbench.agentdto.NodeMonitorDTO;
import com.llmbench.agentdto.SuccessResponse;
import com.llmbench.agentutils.JsonUtils;
import java.io.IOException;
import java.util.List;
import org.apache.log4j.Logger;

public class GpuMonitorCollector {
  private static final String CALLER_SUCCESS = "success";
  private static Logger logger = Logger.getLogger(GpuMonitorCollector.class);
  private static final String MONITOR_OUTPUT_FILE_PATH = "/tmp/gpu_monitor.json";
  private static final String ENABLE_MONITOR = "DISABLE";

  public BaseResponse collectMonitor(String pythonInterpreter ,String monitorScriptPath, String enableMonitor) {
    if (enableMonitor == null) {
      enableMonitor = ENABLE_MONITOR;
    }

    try {
      String[] scriptArgs = new String[] {
              pythonInterpreter,
              monitorScriptPath,
              MONITOR_OUTPUT_FILE_PATH,
              enableMonitor
      };
      ShellCaller caller = new ShellCaller();
      caller.doCall(scriptArgs);
      return getMonitorDataFromFile();
    } catch (IOException | InterruptedException e) {
      return new ErrorResponse("COLLECT_GPU_SCRIPT_FAILED", "", e.getMessage(), "");
    }
  }

  public BaseResponse getMonitorDataFromFile() {
    try {
      String monitorResult = JsonUtils.fileToJson(MONITOR_OUTPUT_FILE_PATH);
      JSONObject monitorResultObj = JSON.parseObject(monitorResult);
      if (null == monitorResultObj) {
        throw new IOException("monitor file is not existed.");
      }
      String responseCode = (String)monitorResultObj.get("code");
      if (CALLER_SUCCESS.equals(responseCode)) {
        JSONArray listMonitorData = (JSONArray)monitorResultObj.get("data");
        return new SuccessResponse(convertMonitorArrayToDTO(listMonitorData), "", "");
      } else {
        String message = (String)monitorResultObj.get("message");
        return new ErrorResponse("COLLECT_GPU_SCRIPT_FAILED", "", message, "");
      }
    } catch (IOException e) {
        return new ErrorResponse("COLLECT_GPU_SCRIPT_FAILED", "", e.getMessage(), "");
      }
  }

  public List<NodeMonitorDTO> convertMonitorArrayToDTO(JSONArray listMonitorData) {
    List<NodeMonitorDTO> listNodeMonitor = JSON.parseArray(listMonitorData.toJSONString(), NodeMonitorDTO.class);
    return listNodeMonitor;
  }
}