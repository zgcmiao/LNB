# Job Execution System - Worker Node Subsystem

The worker node of the Job Execution System receives assigned jobs from the master node and runs the jobs with the
**shortest-job-first scheduling policy**.

## Prerequisites

### Python environment

This system requires Python (version >= `3.10`). Use the following command to install the dependencies.

```bash
pip install -r requirements.txt
```

### Java Runtime

This system requires **Java Runtime Environment(JRE)** or **Java Development Kit(JDK)** (version == `1.8` or `1.11`).

## Run

Please use the following command to run the system with the pre-built JAR package.

```bash
java -jar deployment/agent-api-1.0.0-RELEASE.jar \
    --BACKEND_ADDRESS=http://<MASTER_URL>:8080 \  
    --PYTHON_INTERPRETER=<PYTHON_INTERPRETER> \
    --MONITOR_SCRIPT_PATH=<PROJECT_ROOT_PATH>/deployment/monitor.py \
    --SERIAL_NUM=<SERIAL_NUM> \
    --NFS_PATH=<NFS_PATH>
```

The detailed descriptions of the command line parameters are listed below.

| Parameter           | Description                                                                                                                                        | Required | 
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| BACKEND_ADDRESS     | URL of the Master Node Subsystem                                                                                                                   | Y        |
| PYTHON_INTERPRETER  | The path to the Python interpreter, where the dependencies have been installed                                                                     | Y        |
| MONITOR_SCRIPT_PATH | **Absolute path** to the GPU monitoring script                                                                                                     | Y        |
| SERIAL_NUM          | The **unique** identifier of the worker node                                                                                                       | Y        |
| NFS_PATH            | Path of the shared folder for all the systems. Please refer to the [README of Inference Engine](../../engine/#nfs-shared-folder) for more details. | Y        | 

## Build From Source

See [build.md](build.md) for instructions on building the package from source.
