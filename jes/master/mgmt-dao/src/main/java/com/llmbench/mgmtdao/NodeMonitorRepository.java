package com.llmbench.mgmtdao;

import com.llmbench.mgmtentity.NodeInfo;
import com.llmbench.mgmtentity.NodeMonitor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface NodeMonitorRepository extends JpaRepository<NodeMonitor, Integer> {

  /**
   * Query by SN and GPU number
   *
   * @param serialNum SN
   * @param gpuId     GPU ID
   * @return {@link NodeInfo}
   */
  NodeMonitor findBySerialNumAndGpuId(String serialNum, String gpuId);
}
