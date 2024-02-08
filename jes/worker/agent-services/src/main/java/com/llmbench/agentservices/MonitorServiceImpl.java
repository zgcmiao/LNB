package com.llmbench.agentservices;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.NodeHealthDTO;
import com.llmbench.agentdto.NodeMonitorDTO;
import com.llmbench.agentutils.ConvertUtils;
import com.llmbench.agentutils.HttpClientUtils;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class MonitorServiceImpl implements IMonitorService {

  @Value("${BACKEND_ADDRESS}")
  private String backendAddress;

  /**
   * Report node health status
   *
   * @param nodeHealth node health status
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse postNodeHealth(NodeHealthDTO nodeHealth) {
    Map<String, Object> map = null;
    try {
      map = ConvertUtils.convertObjectToMap(nodeHealth);
    } catch (IllegalAccessException e) {
      throw new RuntimeException(e);
    }
    BaseResponse response = HttpClientUtils.doPost(String.format("%s/api/monitor/node/health", backendAddress), map);
    return response;
  }

  /**
   * Report node monitoring data
   *
   * @param listNodeMonitor node monitoring data
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse postNodeMonitor(List<NodeMonitorDTO> listNodeMonitor) {
    BaseResponse response = HttpClientUtils.doListPost(String.format("%s/api/monitor/node/monitor", backendAddress),
            listNodeMonitor);
    return response;
  }
}
