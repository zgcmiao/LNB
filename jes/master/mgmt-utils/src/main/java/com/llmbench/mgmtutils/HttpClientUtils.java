package com.llmbench.mgmtutils;

import com.llmbench.mgmtdto.BaseResponse;
import com.llmbench.mgmtdto.ErrorResponse;
import com.llmbench.mgmtdto.SuccessResponse;
import java.io.IOException;
import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import org.apache.log4j.Logger;

public class HttpClientUtils {

  public static final String REQUEST_ERROR = "REQUEST_ERROR";
  private static Logger logger = Logger.getLogger(HttpClientUtils.class);

  public static BaseResponse doGet(String url) {
    CloseableHttpClient httpClient = null;
    CloseableHttpResponse response = null;
    String result = "";
    try {
      httpClient = HttpClients.createDefault();
      HttpGet httpGet = new HttpGet(url);
      RequestConfig requestConfig = RequestConfig.custom().setConnectTimeout(35000)
          .setConnectionRequestTimeout(35000)
          .setSocketTimeout(60000)
          .build();
      httpGet.setConfig(requestConfig);
      response = httpClient.execute(httpGet);
      HttpEntity entity = response.getEntity();
      result = EntityUtils.toString(entity);
    } catch (ClientProtocolException e) {
      logger.error(e.getMessage(),e);
      return new ErrorResponse(REQUEST_ERROR, "ClientProtocolException", e.getMessage(), "");
    } catch (IOException e) {
      logger.error(e.getMessage(),e);
      return new ErrorResponse(REQUEST_ERROR, "IOException", e.getMessage(), "");
    } finally {
      if (null != response) {
        try {
          response.close();
        } catch (IOException e) {
          logger.error(e.getMessage(),e);
        }
      }
      if (null != httpClient) {
        try {
          httpClient.close();
        } catch (IOException e) {
          logger.error(e.getMessage(),e);
        }
      }
    }
    return new SuccessResponse(result, "http request get result success.", "");
  }

  public static BaseResponse doPost(String url, Object data) {
    CloseableHttpClient httpClient = null;
    CloseableHttpResponse httpResponse = null;
    String result = "";
    httpClient = HttpClients.createDefault();
    HttpPost httpPost = new HttpPost(url);
    RequestConfig requestConfig = RequestConfig.custom().setConnectTimeout(35000)
            .setConnectionRequestTimeout(35000)
            .setSocketTimeout(60000)
            .build();
    httpPost.setConfig(requestConfig);
    httpPost.addHeader("Content-type", "application/json;charset=utf-8");
    httpPost.setHeader("Accept","application/json");

    String dataString = JsonUtils.toString(data);
    httpPost.setEntity(new StringEntity(dataString, "utf-8"));
    try {
      httpResponse = httpClient.execute(httpPost);
      HttpEntity entity = httpResponse.getEntity();
      result = EntityUtils.toString(entity);
    } catch (ClientProtocolException e) {
      logger.error(e.getMessage(),e);
      return new ErrorResponse(REQUEST_ERROR, "ClientProtocolException", e.getMessage(), "");
    } catch (IOException e) {
      logger.error(e.getMessage(),e);
      return new ErrorResponse(REQUEST_ERROR, "IOException", e.getMessage(), "");
    } finally {
      if (null != httpResponse) {
        try {
          httpResponse.close();
        } catch (IOException e) {
          logger.error(e.getMessage(),e);
        }
      }
      if (null != httpClient) {
        try {
          httpClient.close();
        } catch (IOException e) {
          logger.error(e.getMessage(),e);
        }
      }
    }
    return new SuccessResponse(result, "http request get result success.", "");
  }
}