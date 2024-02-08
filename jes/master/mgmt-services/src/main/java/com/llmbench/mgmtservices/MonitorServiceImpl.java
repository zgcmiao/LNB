package com.llmbench.mgmtservices;

import com.llmbench.mgmtdao.NodeInfoRepository;
import com.llmbench.mgmtdao.NodeMonitorRepository;
import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.ErrorResponse;
import com.llmbench.mgmtdto.FilterDTO;
import com.llmbench.mgmtdto.NodeHealthDTO;
import com.llmbench.mgmtdto.NodeMonitorDTO;
import com.llmbench.mgmtdto.SuccessResponse;
import com.llmbench.mgmtentity.NodeInfo;
import com.llmbench.mgmtentity.NodeMonitor;
import com.llmbench.mgmtutils.CommonUtils;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class MonitorServiceImpl implements IMonitorService {


  @Autowired
  private NodeInfoRepository nodeInfoRepository;

  @Autowired
  private NodeMonitorRepository nodeMonitorRepository;

  /**
   * Report node health status
   *
   * @param nodeHealth node health status
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse postNodeHealth(NodeHealthDTO nodeHealth) {
    String serialNum = nodeHealth.getSerialNum();
    NodeInfo nodeInfo = nodeInfoRepository.findBySerialNum(serialNum);
    Optional<NodeInfo> result = Optional.ofNullable(nodeInfo);

    String resMessage = "";
    if (result.isPresent()) {
      nodeInfo.setUpdatedTime(CommonUtils.getTime());
      resMessage = String.format("update `%s` health status record successful.", serialNum);
    } else {
      nodeInfo = new NodeInfo();
      resMessage = String.format("add `%s` health status record successful.", serialNum);
    }
    BeanUtils.copyProperties(nodeHealth, nodeInfo);
    nodeInfoRepository.save(nodeInfo);
    return new SuccessResponse(null, resMessage, null);
  }

  /**
   * Report node monitoring data
   *
   * @param listNodeMonitor node monitoring data
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse postNodeMonitor(List<NodeMonitorDTO> listNodeMonitor) {
    String resMessage = "";
    if (listNodeMonitor.size() > 0) {
      try {
        ArrayList<NodeMonitor> listNodeMonitorEntity = new ArrayList<>();

        listNodeMonitor.forEach(x -> {
          String serialNum = x.getSerialNum();
          String gpuId = x.getGpuId();
          // Determine whether to add or modify based on SN and GpuId
          NodeMonitor nodeMonitor = nodeMonitorRepository.findBySerialNumAndGpuId(serialNum, gpuId);
          Optional<NodeMonitor> result = Optional.ofNullable(nodeMonitor);
          if (result.isPresent()) {
            nodeMonitor.setUpdatedTime(CommonUtils.getTime());
          } else {
            nodeMonitor = new NodeMonitor();
          }
          BeanUtils.copyProperties(x, nodeMonitor);
          listNodeMonitorEntity.add(nodeMonitor);
        });

        nodeMonitorRepository.saveAll(listNodeMonitorEntity);
        resMessage = String.format("add or update `%s` node monitor records successful.",
                listNodeMonitor.get(0).getSerialNum());
      } catch (Exception ex) {
        return new ErrorResponse("NodeMonitorFailed", "", ex.getMessage(), "");
      }
    } else {
      resMessage = "node monitor is empty.";
    }
    return new SuccessResponse(null, resMessage, null);
  }

  /**
   * Get specified node information
   *
   * @param filter filter
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse listNodeHealth(FilterDTO filter) {
    List<NodeInfo> listNode = nodeInfoRepository.findAll();
    List<NodeHealthDTO> listNodeDTO = new ArrayList<>();
    listNode.forEach(x -> {
      NodeHealthDTO nodeDTO = new NodeHealthDTO();
      BeanUtils.copyProperties(x, nodeDTO);
      listNodeDTO.add(nodeDTO);
    });
    return new SuccessResponse(listNodeDTO, "get node health success.", "");
  }

  /**
   * Get specified node monitoring information
   *
   * @param filter filter
   * @return {@link BaseResponse}
   */
  @Override
  public BaseResponse listNodeMonitor(FilterDTO filter) {
    List<NodeMonitor> listNodeMonitor = nodeMonitorRepository.findAll();
    List<NodeMonitorDTO> listNodeMonitorDTO = new ArrayList<>();
    listNodeMonitor.forEach(x -> {
      NodeMonitorDTO nodeMonitorDTO = new NodeMonitorDTO();
      BeanUtils.copyProperties(x, nodeMonitorDTO);
      listNodeMonitorDTO.add(nodeMonitorDTO);
    });
    return new SuccessResponse(listNodeMonitorDTO, "get node monitor success.", "");
  }
}
