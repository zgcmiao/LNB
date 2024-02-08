import uuid

from sqlalchemy import Column, String, DateTime, Enum, JSON, Text, Integer

from .base import Model
from ..config.enums import TaskTypeEnum, TaskStatusEnum


class TaskTab(Model):
    task_id = Column(String(64), unique=True, primary_key=True, default=uuid.uuid4, nullable=False)
    task_type = Column(Enum(TaskTypeEnum), default=TaskTypeEnum.Inference, nullable=False)
    task_config = Column(JSON, default=dict(), nullable=False)
    model = Column(Text, default='', nullable=False, comment='model list, split by comma')
    model_config = Column(JSON, default=dict(), nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.CREATED, nullable=False)
    progress = Column(JSON, default=dict(), nullable=False)

    start_at = Column(DateTime)
    stop_at = Column(DateTime)
    delete_at = Column(DateTime)


class SubTaskTab(Model):
    sub_task_id = Column(String(64), unique=True, primary_key=True, default=uuid.uuid4, nullable=False)
    task_id = Column(String(64), nullable=False)
    sub_task_config = Column(JSON, default=dict(), nullable=False)
    command = Column(Text, default='', nullable=False)
    model = Column(String(128), default='', nullable=False)
    model_size = Column(Integer, default=0, nullable=False)
    serial_num = Column(String(16), default='', nullable=False)
    output_file_path = Column(String(500), default='', nullable=False)
    output_result = Column(JSON, default=dict(), nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.PENDING, nullable=False)
    progress = Column(JSON, default=dict(), nullable=False)

    start_at = Column(DateTime)
    stop_at = Column(DateTime)
    delete_at = Column(DateTime)
