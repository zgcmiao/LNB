package com.llmbench.agentdto;

public class ErrorResponse extends BaseResponse{
  public ErrorResponse(String errorCode, Object data, String message, String resultId) {
    this.setResponseCode(errorCode);
    this.setMessage(message);
    this.setData(data);
    this.setRequestId(resultId);
  }
}
