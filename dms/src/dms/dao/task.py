from src.dms.dao.base import ModelDAO
from src.dms.models import TaskTab, SubTaskTab


class TaskDAO(ModelDAO[TaskTab]):
    __model_class__ = TaskTab


class SubTaskDAO(ModelDAO[SubTaskTab]):
    __model_class__ = SubTaskTab
