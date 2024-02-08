package com.llmbench.mgmtapi.apis;

import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.NodeHealthDTO;
import com.llmbench.mgmtdto.NodeMonitorDTO;
import com.llmbench.mgmtservices.IMonitorService;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Component(value = "monitorController")
@RequestMapping("/api/monitor")
public class MonitorController {

  @Autowired
  private IMonitorService monitorService;

  /**
   * Report node health status
   *
   * @param nodeHealth node health status
   * @return {@link BaseResponse}
   */
  @PostMapping("/node/health")
  public BaseResponse postNodeHealth(NodeHealthDTO nodeHealth) {
    return this.monitorService.postNodeHealth(nodeHealth);
  }

  /**
   * Report node monitoring data
   *
   * @param listNodeMonitor Node monitoring data
   * @return {@link BaseResponse}
   */
  @PostMapping("/node/monitor")
  public BaseResponse postNodeMonitor(@RequestBody List<NodeMonitorDTO> listNodeMonitor) {
    return this.monitorService.postNodeMonitor(listNodeMonitor);
  }
}
