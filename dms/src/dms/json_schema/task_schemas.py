from src.dms.json_schema import base_schema

CREATE_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'task_type': base_schema.TASK_TYPE_SCHEMA,
        'task_config': {
            'type': 'object',
            'properties': {
                'split_batches': {'type': 'integer', 'minimum': 1},
                'list_subject': {'type': 'array', 'items': base_schema.STRING_SCHEMA},
                'list_shot_type': {'type': 'array', 'items': base_schema.STRING_SCHEMA},
                'subject_absolute_dir': base_schema.STRING_SCHEMA,
                'data_absolute_root': base_schema.STRING_SCHEMA,
                'llm_bench_docker_version': base_schema.STRING_SCHEMA,
                'prefer_subject_prefix': base_schema.STRING_SCHEMA,
            },
            'required': ['data_absolute_root']
        },
        'model': {'type': 'array', 'items': base_schema.STRING_SCHEMA},
        'model_config': {
            'type': 'object'
        }
    },
    'required': ['task_config', 'model', 'model_config']
}

SEARCH_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'page_no': base_schema.PAGE_NO_SCHEMA,
        'count': base_schema.PAGE_COUNT_SCHEMA,
        'task_id': base_schema.UUID_SCHEMA,
        'task_type': base_schema.STRING_SCHEMA,
        'model': base_schema.STRING_SCHEMA,
        'status': base_schema.TASK_STATUS_SCHEMA,
        'start_at_begin': base_schema.DATETIME_SCHEMA,
        'start_at_end': base_schema.DATETIME_SCHEMA,
        'stop_at_begin': base_schema.DATETIME_SCHEMA,
        'stop_at_end': base_schema.DATETIME_SCHEMA,
        'created_at_begin': base_schema.DATETIME_SCHEMA,
        'created_at_end': base_schema.DATETIME_SCHEMA,
        'updated_at_begin': base_schema.DATETIME_SCHEMA,
        'updated_at_end': base_schema.DATETIME_SCHEMA,
    },
    'required': []
}


GET_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'task_id': base_schema.UUID_SCHEMA,
    },
    'required': ['task_id']
}

GET_TOTAL_COUNT_SCHEMA = {
    'type': 'object',
    'properties': {
        'task_id': base_schema.UUID_SCHEMA,
        'task_type': base_schema.STRING_SCHEMA,
        'model': base_schema.STRING_SCHEMA,
        'status': base_schema.TASK_STATUS_SCHEMA,
        'start_at_begin': base_schema.DATETIME_SCHEMA,
        'start_at_end': base_schema.DATETIME_SCHEMA,
        'stop_at_begin': base_schema.DATETIME_SCHEMA,
        'stop_at_end': base_schema.DATETIME_SCHEMA,
        'created_at_begin': base_schema.DATETIME_SCHEMA,
        'created_at_end': base_schema.DATETIME_SCHEMA,
        'updated_at_begin': base_schema.DATETIME_SCHEMA,
        'updated_at_end': base_schema.DATETIME_SCHEMA,
    },
    'required': []
}

UPDATE_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'task_id': base_schema.UUID_SCHEMA,
        'task_type': base_schema.TASK_TYPE_SCHEMA,
        'task_config': base_schema.STRING_SCHEMA,
        'model': {'type': 'array', 'items': base_schema.STRING_SCHEMA},
        'model_config': base_schema.STRING_SCHEMA
    },
    'required': ['task_id']
}

DELETE_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'task_id': base_schema.UUID_SCHEMA,
    },
    'required': ['task_id']
}

SEARCH_SUB_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'page_no': base_schema.PAGE_NO_SCHEMA,
        'count': base_schema.PAGE_COUNT_SCHEMA,
        'task_id': base_schema.UUID_SCHEMA,
        'sub_task_id': base_schema.UUID_SCHEMA,
        'serial_num': base_schema.STRING_SCHEMA,
        'model': base_schema.STRING_SCHEMA,
        'status': base_schema.TASK_STATUS_SCHEMA,
        'start_at_begin': base_schema.DATETIME_SCHEMA,
        'start_at_end': base_schema.DATETIME_SCHEMA,
        'stop_at_begin': base_schema.DATETIME_SCHEMA,
        'stop_at_end': base_schema.DATETIME_SCHEMA,
        'created_at_begin': base_schema.DATETIME_SCHEMA,
        'created_at_end': base_schema.DATETIME_SCHEMA,
        'updated_at_begin': base_schema.DATETIME_SCHEMA,
        'updated_at_end': base_schema.DATETIME_SCHEMA,
    },
    'required': []
}

GET_SUB_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'sub_task_id': base_schema.UUID_SCHEMA,
    },
    'required': ['sub_task_id']
}

GET_TOTAL_SUB_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'task_id': base_schema.UUID_SCHEMA,
        'sub_task_id': base_schema.UUID_SCHEMA,
        'serial_num': base_schema.STRING_SCHEMA,
        'model': base_schema.STRING_SCHEMA,
        'status': base_schema.TASK_STATUS_SCHEMA,
        'start_at_begin': base_schema.DATETIME_SCHEMA,
        'start_at_end': base_schema.DATETIME_SCHEMA,
        'stop_at_begin': base_schema.DATETIME_SCHEMA,
        'stop_at_end': base_schema.DATETIME_SCHEMA,
        'created_at_begin': base_schema.DATETIME_SCHEMA,
        'created_at_end': base_schema.DATETIME_SCHEMA,
        'updated_at_begin': base_schema.DATETIME_SCHEMA,
        'updated_at_end': base_schema.DATETIME_SCHEMA,
    },
    'required': []
}

UPDATE_SUB_TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'sub_task_id': base_schema.UUID_SCHEMA,
        'command': base_schema.STRING_SCHEMA,
        'sub_task_config': base_schema.STRING_SCHEMA,
        'serial_num': base_schema.STRING_SCHEMA,
        'output_file_path': base_schema.STRING_SCHEMA,
        'output_result': base_schema.STRING_SCHEMA,
        'status': base_schema.TASK_STATUS_SCHEMA,
        'progress': base_schema.STRING_SCHEMA,
        'start_at': base_schema.DATETIME_SCHEMA,
        'stop_at': base_schema.DATETIME_SCHEMA,
    },
    'required': ['sub_task_id']
}
