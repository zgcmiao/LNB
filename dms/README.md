# Data Management System

The Data Management System is responsible for data processing, data storage, and receiving user requests.
The Main Controller receives user request and raw data materials, and initializes the benchmark jobs, which are
delivered to the Job Execution System.

## Run with Docker

You may use the [Dockerfile](Dockerfile) to build the image and run the server in a Docker container, *e.g.*

```bash
export NFS_PATH=<NFS_PATH>
docker build -t data_mgmt_sys .
docker run --rm --name data_mgmt_sys -itd -p 8000:8000 -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro -v ${NFS_PATH}:${NFS_PATH} -e NFS_PATH=${NFS_PATH} data_mgmt_sys
```

**Note:** `<NFS_PATH>` is the path of the shared folder for all the systems. Please refer to
the [README of Inference Engine](../engine/#nfs-shared-folder) for more details.

This is the recommended way to run this system. Should you need to deploy it in your local environment, please refer
to [install_local.md](install_local.md).

## APIs

Please refer to [Data Management System APIs](docs/apis/data_management_system_apis.md).

## Reference

For more details, please refer to [reference.md](reference.md).
