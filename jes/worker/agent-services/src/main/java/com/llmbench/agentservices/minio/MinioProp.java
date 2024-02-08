package com.llmbench.agentservices.minio;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@ConfigurationProperties(prefix = "minio")
@Component
public class MinioProp {
  private String endpoint;
  private String accesskey;
  private String secretKey;
}