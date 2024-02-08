package com.llmbench.mgmtdao;

import com.llmbench.mgmtentity.NodeInfo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface NodeInfoRepository extends JpaRepository<NodeInfo, Integer> {

  /**
   * Search by SN number
   *
   * @param serialNum Node SN number
   * @return {@link NodeInfo}
   */
  NodeInfo findBySerialNum(String serialNum);
}
