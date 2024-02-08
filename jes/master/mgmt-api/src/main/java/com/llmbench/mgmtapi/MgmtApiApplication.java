package com.llmbench.mgmtapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = {"com.llmbench.mgmtapi"})
@ComponentScan("com.llmbench.mgmtservices")
@ComponentScan("com.llmbench.mgmtjob")
@ComponentScan("com.llmbench.mgmtdto")
@EntityScan("com.llmbench.mgmtentity")
@EnableJpaRepositories("com.llmbench.mgmtdao")
@EnableScheduling
public class MgmtApiApplication {

  public static void main(String[] args) {
    SpringApplication.run(MgmtApiApplication.class, args);
  }
}
