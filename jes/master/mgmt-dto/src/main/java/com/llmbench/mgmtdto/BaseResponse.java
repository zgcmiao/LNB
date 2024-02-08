package com.llmbench.mgmtdto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class BaseResponse {
  @JsonProperty("responseCode")
  private String responseCode;

  @JsonProperty("Message")
  private String message;

  @JsonProperty("data")
  private Object data;

  @JsonProperty("requestId")
  private String requestId;
}
