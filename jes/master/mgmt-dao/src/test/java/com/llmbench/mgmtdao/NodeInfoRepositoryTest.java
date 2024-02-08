package com.llmbench.mgmtdao;

import static org.junit.Assert.assertEquals;

import com.llmbench.mgmtentity.NodeInfo;
import javax.annotation.Resource;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

@RunWith(SpringRunner.class)
@SpringBootTest(classes = DaoApplicationTests.class)
public class NodeInfoRepositoryTest {
  @Resource
  private NodeInfoRepository nodeInfoRepository;

  private void setUp() {
    NodeInfo nodeInfo = new NodeInfo();
    nodeInfo.setSerialNum("sn-001");
    nodeInfo.setStatus("ok");
    this.nodeInfoRepository.save(nodeInfo);
  }

  @Test
  public void testAdd() {
    setUp();
    assertEquals(1, this.nodeInfoRepository.findAll().size());
  }
}
