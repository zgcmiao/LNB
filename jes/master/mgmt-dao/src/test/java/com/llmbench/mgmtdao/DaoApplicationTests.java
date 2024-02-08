package com.llmbench.mgmtdao;

import org.junit.Test;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication
@EntityScan("com.llmbench.mgmtentity")
@EnableJpaRepositories("com.llmbench.mgmtdao")
public class DaoApplicationTests {
  @Test
  public void contextLoads() {
  }
}
