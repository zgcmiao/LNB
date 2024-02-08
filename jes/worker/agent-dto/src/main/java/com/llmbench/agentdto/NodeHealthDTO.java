package com.llmbench.agentdto;

import java.io.Serializable;
import lombok.Data;

@Data
public class NodeHealthDTO implements Serializable {
  private String serialNum;
  private String status;
}
