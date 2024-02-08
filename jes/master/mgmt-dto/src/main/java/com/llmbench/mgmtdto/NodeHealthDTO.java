package com.llmbench.mgmtdto;

import java.io.Serializable;
import lombok.Data;

@Data
public class NodeHealthDTO implements Serializable {

  private static final long serialVersionUID = -2403400204278535641L;
  private String serialNum;
  private String status;
}
