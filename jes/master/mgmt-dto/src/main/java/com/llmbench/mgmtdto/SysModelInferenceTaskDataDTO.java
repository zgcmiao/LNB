package com.llmbench.mgmtdto;

import java.util.List;
public class SysModelInferenceTaskDataDTO {

  private int count;
  private List<SysModelInferenceTaskDataObjectDTO> list;
  private int page_no;
  public void setCount(int count) {
    this.count = count;
  }
  public int getCount() {
    return count;
  }

  public void setList(List<SysModelInferenceTaskDataObjectDTO> list) {
    this.list = list;
  }
  public List<SysModelInferenceTaskDataObjectDTO> getList() {
    return list;
  }

  public void setPage_no(int page_no) {
    this.page_no = page_no;
  }
  public int getPage_no() {
    return page_no;
  }

}