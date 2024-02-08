package com.llmbench.agentutils;

import com.alibaba.fastjson.JSON;
import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.ErrorResponse;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.apache.http.HttpEntity;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
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
//    logger.info(result);
    BaseResponse responseResult = JSON.parseObject(result, BaseResponse.class);
    return responseResult;
  }

  public static BaseResponse doPost(String url, Map<String, Object> paramMap) {
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
    httpPost.addHeader("Content-Type", "application/x-www-form-urlencoded");
    if (null != paramMap && paramMap.size() > 0) {
      List<NameValuePair> nvps = new ArrayList<NameValuePair>();
      Set<Map.Entry<String, Object>> entrySet = paramMap.entrySet();
      Iterator<Map.Entry<String, Object>> iterator = entrySet.iterator();
      while (iterator.hasNext()) {
        Map.Entry<String, Object> mapEntry = iterator.next();
        nvps.add(new BasicNameValuePair(mapEntry.getKey(), mapEntry.getValue().toString()));
      }

      try {
        httpPost.setEntity(new UrlEncodedFormEntity(nvps, "UTF-8"));
      } catch (UnsupportedEncodingException e) {
        logger.error(e.getMessage(),e);
      }
    }
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
    BaseResponse responseResult = JSON.parseObject(result, BaseResponse.class);
    return responseResult;
  }

  public static BaseResponse doListPost(String url, List<?> listData) {
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

    String dataString = JsonUtils.toString(listData);
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
//    logger.info(result);
    BaseResponse responseResult = JSON.parseObject(result, BaseResponse.class);
    return responseResult;
  }
}