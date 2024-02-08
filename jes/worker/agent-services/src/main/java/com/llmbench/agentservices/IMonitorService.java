package com.llmbench.agentservices;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.NodeHealthDTO;
import com.llmbench.agentdto.NodeMonitorDTO;
import java.util.List;

public interface IMonitorService {

  /**
   * Report node health status
   *
   * @param nodeHealth node health status
   * @return {@link BaseResponse}
   */
  BaseResponse postNodeHealth(NodeHealthDTO nodeHealth);

  /**
   * Report node monitoring data
   *
   * @param listNodeMonitor node monitoring data
   * @return {@link BaseResponse}
   */
  BaseResponse postNodeMonitor(List<NodeMonitorDTO> listNodeMonitor);
}
