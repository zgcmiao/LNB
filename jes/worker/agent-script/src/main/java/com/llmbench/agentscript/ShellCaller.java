package com.llmbench.agentscript;

import com.llmbench.agentdto.BaseResponse;
import com.llmbench.agentdto.ErrorResponse;
import com.llmbench.agentdto.SuccessResponse;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import org.apache.log4j.Logger;

public class ShellCaller {

  private static Logger logger = Logger.getLogger(ShellCaller.class);

  public BaseResponse doCall(String[] scriptArgs) throws InterruptedException, IOException {
    Integer exitValue = 0;
    try {
      Process doScriptProc = Runtime.getRuntime().exec(scriptArgs);

      StringBuilder processResult = new StringBuilder();
      StringBuilder processErrorResult = new StringBuilder();

      InputStream inputStream = doScriptProc.getInputStream();
      BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
      String line = "";
      while ((line = reader.readLine()) != null) {
        processResult.append(line);
      }
      InputStream errorStream = doScriptProc.getErrorStream();
      BufferedReader errorReader = new BufferedReader(new InputStreamReader(errorStream));
      String error;
      while ((error = errorReader.readLine()) != null) {
        processErrorResult.append(error);
      }

      reader.close();
      errorReader.close();

      exitValue = doScriptProc.waitFor();
      if (exitValue == 0) {
        return new SuccessResponse(processResult.toString(), "", "");
      } else {
        return new ErrorResponse("SHELL_CALL_FAILED", "", processErrorResult.toString(), "");
      }
    } catch (IOException e) {
      e.printStackTrace();
      return new ErrorResponse("SHELL_CALL_FAILED", "", e.getMessage(), "");
    } catch (InterruptedException e) {
      e.printStackTrace();
      return new ErrorResponse("SHELL_CALL_FAILED", "", e.getMessage(), "");
    }
  }
}