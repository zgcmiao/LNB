package com.llmbench.mgmtservices;

import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.FilterDTO;
import com.llmbench.mgmtdto.NodeHealthDTO;
import com.llmbench.mgmtdto.NodeMonitorDTO;
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

  /**
   * Get specified node information
   *
   * @param filter filter
   * @return {@link BaseResponse}
   */
  BaseResponse listNodeHealth(FilterDTO filter);

  /**
   * Get specified node monitoring information
   *
   * @param filter filter
   * @return {@link BaseResponse}
   */
  BaseResponse listNodeMonitor(FilterDTO filter);
}
