package com.llmbench.agentapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = {"com.llmbench.agentapi"})
@ComponentScan("com.llmbench.agentservices")
@ComponentScan("com.llmbench.agentjob")
@ComponentScan("com.llmbench.agentdto")
@EntityScan("com.llmbench.agententity")
@EnableJpaRepositories("com.llmbench.agentdao")
@EnableScheduling
public class AgentApiApplication {

  public static void main(String[] args) {
    SpringApplication.run(AgentApiApplication.class, args);
  }
}
