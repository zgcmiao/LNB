# Data Management System APIs

## Tables of Contents

- [Create Task](#create-task)
- [Search Task List](#search-task-list)
- [Get Total Count Task](#get-total-count-task)
- [Get Task Details](#get-task-details)
- [Update Task](#update-task)
- [Delete Task](#delete-task)
- [Search Sub-Task List](#search-sub-task-list)
- [Get Total Count Sub-Task](#get-total-count-sub-task)
- [Get Sub-Task Details](#get-sub-task-details)
- [Update Sub-Task](#update-sub-task)

## Create Task

Create task

### Request
`POST` /api/task/create

```json
{
    "task_config": {
        "split_batches": 10000,
        "list_shot_type": ["zero-shot"],
        "data_absolute_root": "<NFS_PATH>/question_bank/written_exam/mcq.json",
        "llm_bench_docker_version":"release",
        "llm_bench_version":"logits"
    },
    "model": ["huggyllama/llama-7b"],
    "model_config": {"huggyllama/llama-7b": {"model_size": 7}}
}
```

### Params

| Parameter    | Description         | Data Type | Necessary | Example                  | Remark                          |
|--------------|---------------------|-----------|-----------|--------------------------|---------------------------------|
| task_type    | task type           | string    | N         | Inference                | TaskTypeEnum, include：Inference |
| task_config  | task configuration  | dict      | N         | {}                       |                                 |
| model        | model list          | list      | Y         | ["huggyllama/llama-13b"] |                                 |
| model_config | model configuration | dict      | N         |                          |                                 |

The structure of task_config is as follows: 

| Parameter                | Data Type | Necessary | Example              | Description                                                                                                                                          |
|--------------------------|-----------|-----------|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| split_batches            | int       | N         | 1000                 | When splitting into subtasks, the maximum number of questions for each subtask                                                                       |
| list_shot_type           | list      | N         | ["zero-shot"]        | all shot_type                                                                                                                                        |
| data_absolute_root       | string    | Y         | "/home/xxx/mcq.json" | The absolute address of the data                                                                                                                     |
| llm_bench_docker_version | string    | N         | "release"            | docker version for used dms docker image.                                                                                                            |
| llm_bench_version        | string    | N         | "regex"              | llm_bench version                                                                                                                                    |
| rag                      | bool      | N         | true                 | whether use rag                                                                                                                                      |
| cot                      | bool      | N         | false                | whether use cot                                                                                                                                      |
| prefer_subject_prefix    | string    | N         | "subject_str"        | The subject of the split subtask. This field is used for the `id` in the source and the field splicing of the subject name of the generated subtask. |

The structure of task_config should contain all model in `model` param, and contain `model_size` for each model. Formatting as `{<model_name>: {"model_size": <model_size>}}`, examples: `{"huggyllama/llama-13b": {"model_size": 13}}`

### Return
```json
{
    "code": "0",
    "data": {
        "task_id": "cf374864-6843-4c96-a279-296e7021ec8f"
    },
    "message": "Success"
}
```

## Search Task List

search task list

### Request

`GET /api/task/list`

### Params

| Parameter        | Description             | Data Type | Necessary  | Example                                | Remark                                                                                 |
|------------------|-------------------------|-----------|------------|----------------------------------------|----------------------------------------------------------------------------------------|
| page_no          | page number             | int       | N          | 1                                      | default: 1                                                                             |
| count            | count for per page      | int       | N          | 10                                     | default: 10                                                                            |
| need_pagination  | whether need pagination | bool      | N          | False                                  | default: True                                                                          |
| task_id          | task ID                 | string    | N          | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |                                                                                        |
| task_type        | task type               | string    | N          | Inference                              | enum: Inference                                                                        |
| model            | model name              | string    | N          | "huggyllama/llama-13b"                 | fuzzy matching                                                                         |
| status           | task status             | string    | N          | PENDING                                | enum: CREATED, PENDING, RUNNING, SUCCESS, FAILED, DONE, EXECUTED, INTERRUPT, OPERATION |
| start_at_begin   | task start time begin   | Datetime  | N          | 2023-11-25                             |                                                                                        |
| start_at_end     | task start time end     | Datetime  | N          | 2023-11-28                             |                                                                                        |
| stop_at_begin    | task stop time begin    | Datetime  | N          | 2023-11-25                             |                                                                                        |
| stop_at_end      | task stop time end      | Datetime  | N          | 2023-11-28                             |                                                                                        |
| created_at_begin | task created time begin | Datetime  | N          | 2023-11-25                             |                                                                                        |
| created_at_end   | task created time end   | Datetime  | N          | 2023-11-28                             |                                                                                        |
| updated_at_begin | task updated time begin | Datetime  | N          | 2023-11-25                             |                                                                                        |
| updated_at_end   | task updated time end   | Datetime  | N          | 2023-11-28                             |                                                                                        |

### Return

```json
{
    "code": "0",
    "data": {
        "count": 10,
        "list": [
            {
                "created_at": "2023-11-27 07:26:43",
                "delete_at": "None",
                "model": "huggyllama/llama-13b",
                "model_config": "{}",
                "progress": "{'count': 0, 'total': 0}",
                "start_at": "None",
                "status": "PENDING",
                "stop_at": "None",
                "sub_task_id_list": [
                    "ba4e2ac6-121b-4bd6-b85a-821eaeea9717"
                ],
                "task_config": "{\"list_shot_type\": [\"zero-shot\"],  \"data_absolute_root\": \"/home/xxx/mcq.json\"}",
                "task_id": "38097c30-cf27-4ff8-83e6-f43d5be01fd8",
                "task_type": "Inference",
                "updated_at": "2023-11-27 08:47:05"
            }
        ],
        "page_no": 1
    },
    "message": "Success"
}
```

## Get Total Count Task

get total task

### Request

`GET /api/task/total`

### Params

| Parameter        | Description             | Data Type | Necessary | Example                                | Remark                                                                                 |
|------------------|-------------------------|-----------|-----------|----------------------------------------|----------------------------------------------------------------------------------------|
| task_id          | task ID                 | string    | N         | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |                                                                                        |
| task_type        | task type               | string    | N         | Inference                              | enum: Inference                                                                        |
| model            | model name              | string    | N         | "huggyllama/llama-13b"                 | fuzzy matching                                                                         |
| status           | task status             | string    | N         | PENDING                                | enum: CREATED, PENDING, RUNNING, SUCCESS, FAILED, DONE, EXECUTED, INTERRUPT, OPERATION |
| start_at_begin   | task start time begin   | Datetime  | N         | 2023-11-25                             |                                                                                        |
| start_at_end     | task start time end     | Datetime  | N         | 2023-11-28                             |                                                                                        |
| stop_at_begin    | task stop time begin    | Datetime  | N         | 2023-11-25                             |                                                                                        |
| stop_at_end      | task stop time end      | Datetime  | N         | 2023-11-28                             |                                                                                        |
| created_at_begin | task created time begin | Datetime  | N         | 2023-11-25                             |                                                                                        |
| created_at_end   | task created time end   | Datetime  | N         | 2023-11-28                             |                                                                                        |
| updated_at_begin | task updated time begin | Datetime  | N         | 2023-11-25                             |                                                                                        |
| updated_at_end   | task updated time end   | Datetime  | N         | 2023-11-28                             |                                                                                        |

### Return

```json
{
    "code": "0",
    "data": {
        "total": 2
    },
    "message": "Success"
}
```

## Get Task Details

search task detail

### Request

`GET /api/task/detail`

### Params

| Parameter  | Description | Data Type  | Necessary  | Example                                | Remark  |
|------------|-------------|------------|------------|----------------------------------------|---------|
| task_id    | task ID     | string     | Y          | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |         |

### Return

```json
{
    "code": "0",
    "data": {
        "created_at": "2023-11-27 07:26:43",
        "delete_at": "None",
        "model": "huggyllama/llama-13b",
        "model_config": "{}",
        "progress": "{'count': 0, 'total': 0}",
        "start_at": "None",
        "status": "PENDING",
        "stop_at": "None",
        "task_config": "{\"list_shot_type\": [\"zero-shot\"],  \"data_absolute_root\": \"/home/xxx/mcq.json\"}",
        "task_id": "38097c30-cf27-4ff8-83e6-f43d5be01fd8",
        "sub_task_id_list": ["ba4e2ac6-121b-4bd6-b85a-821eaeea9717"],
        "task_type": "Inference",
        "updated_at": "2023-11-27 08:47:05"
    },
    "message": "Success"
}
```

## Update Task

update task information

### Request

`POST /api/task/update`

```json
{
    "task_id": "cf374864-6843-4c96-a279-296e7021ec8f",
    "model": ["huggyllama/llama-30b", "huggyllama/llama-13b"]
}
```

### Params

| Parameter    | Description         | Data Type | Necessary | Example                                | Remark                           |
|--------------|---------------------|-----------|-----------|----------------------------------------|----------------------------------|
| task_id      | task ID             | string    | Y         | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |                                  |
| task_type    | task type           | string    | N         | Inference                              | TaskTypeEnum, include: Inference |
| task_config  | task configuration  | string    | N         | "{}"                                   |                                  |
| model        | model list          | list      | Y         | ["huggyllama/llama-13b"]               |                                  |
| model_config | model configuration | string    | N         | "{}"                                   |                                  |

### Return

```json
{
    "code": "0",
    "data": {
    },
    "message": "Success"
}
```


## Delete Task

delete task

### Request

`POST /api/task/delete`

```json
{
    "task_id": "cf374864-6843-4c96-a279-296e7021ec8f"
}
```

### Params

| Parameter | Description | Data Type | Necessary | Example                                | Remark |
|-----------|-------------|-----------|-----------|----------------------------------------|--------|
| task_id   | task ID     | string    | Y         | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |        |

### Return

```json
{
    "code": "0",
    "data": {
    },
    "message": "Success"
}
```


## Search Sub-Task List

search sub-task list

### Request

`GET /api/task/sub_task/list`

### Params

| Parameter        | Description                                        | Data Type | Necessary | Example                                | Remark                                                                                 |
|------------------|----------------------------------------------------|-----------|-----------|----------------------------------------|----------------------------------------------------------------------------------------|
| page_no          | page number                                        | int       | N         | 1                                      | default: 1                                                                             |
| count            | count per page                                     | int       | N         | 10                                     | default: 10                                                                            |
| need_pagination  | whether need pagination                            | bool      | N         | False                                  | default: True                                                                          |
| task_id          | task ID                                            | string    | N         | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |                                                                                        |
| sub_task_id      | sub-task ID                                        | string    | N         | "007c30-cf27-4ff8-83e6-f43d5be01fd8"   |                                                                                        |
| serial_num       | The server serial number on which the subtask runs | string    | N         | "sn-001"                               | enum: Inference                                                                        |
| status           | sub-task status                                    | string    | N         | PENDING                                | enum: CREATED, PENDING, RUNNING, SUCCESS, FAILED, DONE, EXECUTED, INTERRUPT, OPERATION |
| start_at_begin   | sub-task start time begin                          | Datetime  | N         | 2023-11-25                             |                                                                                        |
| start_at_end     | sub-task start time end                            | Datetime  | N         | 2023-11-28                             |                                                                                        |
| stop_at_begin    | sub-task stop time begin                           | Datetime  | N         | 2023-11-25                             |                                                                                        |
| stop_at_end      | sub-task stop time end                             | Datetime  | N         | 2023-11-28                             |                                                                                        |
| created_at_begin | sub-task created time begin                        | Datetime  | N         | 2023-11-25                             |                                                                                        |
| created_at_end   | sub-task created time end                          | Datetime  | N         | 2023-11-28                             |                                                                                        |
| updated_at_begin | sub-task updated time begin                        | Datetime  | N         | 2023-11-25                             |                                                                                        |
| updated_at_end   | sub-task updated time end                          | Datetime  | N         | 2023-11-28                             |                                                                                        |

### Return

```json
{
    "code": "0",
    "data": {
        "count": "1",
        "list": [
            {
                "command": "docker run -v ~/.cache/huggingface/hub/models--huggyllama--llama-13b:/root/.cache/huggingface/hub/models--huggyllama--llama-13b -v /tmp/{sub_task_id}/output:/llm-bench/output --gpus all --name llmbench-4614ac8d-b316-41c1-921d-b134b542d5c0-15 -e PYTHONPATH=/llm-bench llm-bench:1.0.18 python3 run_models.py --list_model huggyllama/llama-13b --list_subject security-4614ac8d-b316-41c1-921d-b134b542d5c0-15 --list_shot_type zero-shot --no-dry_run",
                "created_at": "2023-12-05 08:48:48",
                "delete_at": "None",
                "model": "huggyllama/llama-13b",
                "model_size": "13",
                "output_file_path": "",
                "output_result": "{}",
                "progress": "{}",
                "serial_num": "",
                "start_at": "None",
                "status": "PENDING",
                "stop_at": "None",
                "sub_task_config": "{\"split_batches\": 100, \"list_subject\": [\"security-4614ac8d-b316-41c1-921d-b134b542d5c0-15\"], \"list_shot_type\": [\"zero-shot\"], \"data_absolute_root\": \"/home/xxx/mcq.json\", \"subject_absolute_file_path\": \"/tmp/llm-bench-result/4614ac8d-b316-41c1-921d-b134b542d5c0/subjects/security-4614ac8d-b316-41c1-921d-b134b542d5c0-15.json\", \"data_absolute_file_path\": \"/tmp/llm-bench-result/4614ac8d-b316-41c1-921d-b134b542d5c0/source/4614ac8d-b316-41c1-921d-b134b542d5c0/4614ac8d-b316-41c1-921d-b134b542d5c0-15.json\", \"list_model\": [\"huggyllama/llama-13b\"]}",
                "sub_task_id": "0b0d2585-6425-4a0b-8602-cbe0ec65b352",
                "task_id": "4614ac8d-b316-41c1-921d-b134b542d5c0",
                "updated_at": "2023-12-05 08:48:48"
            }
        ],
        "page_no": 1
    },
    "message": "Success"
}
```

## Get Total Count Sub-Task

get sub-task total count

### Request

`GET /api/task/sub_task/total`

### Params

| Parameter        | Description                                        | Data Type | Necessary | Example                                | Remark                                                                                 |
|------------------|----------------------------------------------------|-----------|-----------|----------------------------------------|----------------------------------------------------------------------------------------|
| task_id          | task ID                                            | string    | N         | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |                                                                                        |
| sub_task_id      | sub-task ID                                        | string    | N         | "007c30-cf27-4ff8-83e6-f43d5be01fd8"   |                                                                                        |
| serial_num       | The server serial number on which the subtask runs | string    | N         | "sn-001"                               | enum: Inference                                                                        |
| status           | sub-task status                                    | string    | N         | PENDING                                | enum: CREATED, PENDING, RUNNING, SUCCESS, FAILED, DONE, EXECUTED, INTERRUPT, OPERATION |
| start_at_begin   | sub-task start time begin                          | Datetime  | N         | 2023-11-25                             |                                                                                        |
| start_at_end     | sub-task start time end                            | Datetime  | N         | 2023-11-28                             |                                                                                        |
| stop_at_begin    | sub-task stop time begin                           | Datetime  | N         | 2023-11-25                             |                                                                                        |
| stop_at_end      | sub-task stop time end                             | Datetime  | N         | 2023-11-28                             |                                                                                        |
| created_at_begin | sub-task created time begin                        | Datetime  | N         | 2023-11-25                             |                                                                                        |
| created_at_end   | sub-task created time end                          | Datetime  | N         | 2023-11-28                             |                                                                                        |
| updated_at_begin | sub-task updated time begin                        | Datetime  | N         | 2023-11-25                             |                                                                                        |
| updated_at_end   | sub-task updated time end                          | Datetime  | N         | 2023-11-28                             |                                                                                        |

### Return

```json
{
    "code": "0",
    "data": {
        "total": 33
    },
    "message": "Success"
}
```

## Get Sub-Task Details

get sub-task detail

### Request

`GET /api/task/sub_task/detail`

```json
{
  "sub_task_id": "0b0d2585-6425-4a0b-8602-cbe0ec65b352"
}
```

### Params

| Parameter   | Description | Data Type | Necessary | Example                                | Remark |
|-------------|-------------|-----------|-----------|----------------------------------------|--------|
| sub_task_id | sub-task ID | string    | Y         | "38097c30-cf27-4ff8-83e6-f43d5be01fd8" |        |

### Return

```json
{
    "code": "0",
    "data": {
        "command": "docker run -v ~/.cache/huggingface/hub/models--huggyllama--llama-13b:/root/.cache/huggingface/hub/models--huggyllama--llama-13b -v /tmp/{sub_task_id}/output:/llm-bench/output --gpus all --name llmbench-4614ac8d-b316-41c1-921d-b134b542d5c0-15 -e PYTHONPATH=/llm-bench llm-bench:1.0.18 python3 run_models.py --list_model huggyllama/llama-13b --list_subject security-4614ac8d-b316-41c1-921d-b134b542d5c0-15 --list_shot_type zero-shot --no-dry_run",
        "created_at": "2023-12-05 08:48:48",
        "delete_at": "None",
        "model": "huggyllama/llama-13b",
        "model_size": "13",
        "output_file_path": "",
        "output_result": "{}",
        "progress": "{}",
        "serial_num": "",
        "start_at": "None",
        "status": "PENDING",
        "stop_at": "None",
        "sub_task_config": "{\"split_batches\": 100, \"list_subject\": [\"security-4614ac8d-b316-41c1-921d-b134b542d5c0-15\"], \"list_shot_type\": [\"zero-shot\"], \"data_absolute_root\": \"/home/xxx/mcq.json\", \"subject_absolute_file_path\": \"/tmp/llm-bench-result/4614ac8d-b316-41c1-921d-b134b542d5c0/subjects/security-4614ac8d-b316-41c1-921d-b134b542d5c0-15.json\", \"data_absolute_file_path\": \"/tmp/llm-bench-result/4614ac8d-b316-41c1-921d-b134b542d5c0/source/4614ac8d-b316-41c1-921d-b134b542d5c0/4614ac8d-b316-41c1-921d-b134b542d5c0-15.json\", \"list_model\": [\"huggyllama/llama-13b\"]}",
        "sub_task_id": "0b0d2585-6425-4a0b-8602-cbe0ec65b352",
        "task_id": "4614ac8d-b316-41c1-921d-b134b542d5c0",
        "updated_at": "2023-12-05 08:48:48"
    },
    "message": "Success"
}
```

## Update Sub Task

update sub task information


### Request

`POST /api/task/sub_task/update`

```json
{
    "sub_task_id": "156f4718-fe94-4adc-966e-150245dc5093",
    "serial_num": "sn-001",
    "start_at": "2023-12-04"
}
```

### Params

| Parameter        | Description               | Data Type | Necessary | Example                                | Remark                                            |
|------------------|---------------------------|-----------|-----------|----------------------------------------|---------------------------------------------------|
| sub_task_id      | sub-task ID               | string    | Y         | "156f4718-fe94-4adc-966e-150245dc5093" |                                                   |
| command          | task command              | string    | N         | ""                                     | Values from `TaskTypeEnum`，including: `Inference` |
| sub_task_config  | sub-task configuration    | string    | N         | "{}"                                   |                                                   |
| serial_num       | serial_num                | string    | N         | ""                                     |                                                   |
| output_file_path | output file path          | string    | N         | ""                                     |                                                   |
| output_result    | output result information | string    | N         | "{}"                                   |                                                   |
| status           | sub-task status           | string    | N         | "RUNNING"                              |                                                   |
| progress         | progress information      | string    | N         | "{}"                                   |                                                   |
| start_at         | start time                | datetime  | N         | "2023-12-20 08:00:00"                  |                                                   |
| stop_at          | end time                  | datetime  | N         | "2023-12-20 10:00:00"                  |                                                   |

### Return

```json
{
    "code": "0",
    "data": {
    },
    "message": "Success"
}
```
