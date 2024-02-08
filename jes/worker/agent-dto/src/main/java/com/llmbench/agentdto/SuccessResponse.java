package com.llmbench.agentdto;

public class SuccessResponse extends BaseResponse{
  public SuccessResponse(Object data, String message, String resultId) {
    this.setResponseCode("success");
    this.setMessage(message);
    this.setData(data);
    this.setRequestId(resultId);
  }
}
