from src.dms.config.enums import TaskTypeEnum, TaskStatusEnum

STRING_SCHEMA = {'type': 'string'}
DATETIME_SCHEMA = {'type': 'string', 'format': 'date-time'}

PAGE_NO_SCHEMA = {'type': 'integer', 'minimum': 1}
PAGE_COUNT_SCHEMA = {'type': 'integer', 'minimum': 1}

TASK_TYPE_SCHEMA = {'type': 'string', 'enum': [e.value for e in TaskTypeEnum]}
TASK_STATUS_SCHEMA = {'type': 'string', 'enum': [e.value for e in TaskStatusEnum]}
UUID_SCHEMA = {'type': 'string', 'minLength': 16, 'maxLength': 64}

