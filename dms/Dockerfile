
FROM ubuntu:22.04
WORKDIR /llm-bench-sys/

ENV FLASK_ENV=${FLASK_ENV}
ENV NFS_PATH=${NFS_PATH}
ENV TimeZone=Asia/Shanghai

ADD manager.py /llm-bench-sys/
ADD run.sh /llm-bench-sys/
ADD requirements.txt /llm-bench-sys/
ADD src /llm-bench-sys/src
ADD flask-script /llm-bench-sys/flask-script

RUN ln -snf /usr/share/zoneinfo/$TimeZone /etc/localtime && echo $TimeZone > /etc/timezon

RUN sed -i s/archive.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list &&  \
    sed -i s/security.ubuntu.com/mirrors.aliyun.com/g /etc/apt/sources.list &&  \
    apt-get -y update && apt-get -y upgrade
RUN apt-get install -y python3-pip python3.10 default-libmysqlclient-dev build-essential vim 
RUN apt-get install -y python3.11-dev
RUN apt-get install -y pkg-config
RUN apt-get install -y net-tools
RUN apt-get install -y iputils-ping
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN pip install -e /llm-bench-sys/flask-script
RUN mkdir -p /tmp/llm-bench-sys/log/

RUN chmod +x /llm-bench-sys/run.sh

ENTRYPOINT ["./run.sh"]
#
EXPOSE 8000
#
#CMD ["/bin/bash"]
