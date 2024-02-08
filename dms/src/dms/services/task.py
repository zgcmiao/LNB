import json

from sqlalchemy import and_

from src.dms.config.enums import TaskStatusEnum, TaskTypeEnum
from src.dms.dao.task import TaskDAO, SubTaskDAO
from src.dms.models import TaskTab, SubTaskTab
from src.dms.services.base import Service
from src.dms.utils.common_utils import model_to_dict


class TaskService(Service):
    @classmethod
    def search_task_list(cls, task_data):
        page_no = task_data.get('page_no', 1)
        count = task_data.get('count', 10)
        need_pagination = task_data.get('need_pagination', True)

        task_id = task_data.get('task_id')
        task_type = task_data.get('task_type')
        model = task_data.get('model')
        status = task_data.get('status')
        start_at_begin = task_data.get('start_at_begin')
        start_at_end = task_data.get('start_at_end')
        stop_at_begin = task_data.get('stop_at_begin')
        stop_at_end = task_data.get('stop_at_end')

        created_at_begin = task_data.get('created_at_begin')
        created_at_end = task_data.get('created_at_end')
        updated_at_begin = task_data.get('updated_at_begin')
        updated_at_end = task_data.get('updated_at_end')

        offset = (int(page_no) - 1) * int(count)

        filters = []
        if task_id is not None:
            filters.append(TaskTab.task_id == task_id)
        if task_type is not None:
            filters.append(TaskTab.task_type == task_type)
        if model is not None:
            filters.append(TaskTab.model.like(f"%{model}%"))
        if status is not None:
            if isinstance(status, TaskStatusEnum):
                filters.append(TaskTab.status == status)
            elif isinstance(status, list):
                filters.append(TaskTab.status.in_(status))
        elif status is None:
            filters.append(TaskTab.status != TaskStatusEnum.DELETED)
        if start_at_begin is not None:
            filters.append(TaskTab.start_at >= start_at_begin)
        if start_at_end is not None:
            filters.append(TaskTab.start_at <= start_at_end)
        if stop_at_begin is not None:
            filters.append(TaskTab.stop_at >= stop_at_begin)
        if stop_at_end is not None:
            filters.append(TaskTab.stop_at <= stop_at_end)
        if created_at_begin is not None:
            filters.append(TaskTab.created_at >= created_at_begin)
        if created_at_end is not None:
            filters.append(TaskTab.created_at <= created_at_end)
        if updated_at_begin is not None:
            filters.append(TaskTab.updated_at >= updated_at_begin)
        if updated_at_end is not None:
            filters.append(TaskTab.updated_at <= updated_at_end)

        if need_pagination:
            task_list = TaskDAO.get_list(filters=[and_(*filters)], offset=offset, limit=count)
        else:
            task_list = TaskDAO.get_list(filters=[and_(*filters)])
        task_info_list = []
        for task_info in task_list:
            sub_task_id_list = SubTaskService.get_sub_task_by_task_id(task_info.task_id)
            task_data = model_to_dict(task_info)
            task_data['sub_task_id_list'] = sub_task_id_list
            task_info_list.append(task_data)
        return {
            'list': task_info_list,
            'page_no': page_no,
            'count': count,
        }

    @classmethod
    def get_task_by_id(cls, task_id):
        task_info = TaskDAO.get_list(filters=[and_(TaskTab.task_id == task_id, TaskTab.status != TaskStatusEnum.DELETED)])
        if task_info.first():
            task_data = model_to_dict(task_info.first())
            sub_task_id_list = SubTaskService.get_sub_task_by_task_id(task_data['task_id'])
            task_data['sub_task_id_list'] = sub_task_id_list
            return task_data
        else:
            return {}

    @classmethod
    def create_task(cls, task_data):
        task_type = task_data.get('task_type', TaskTypeEnum.Inference)
        task_config = json.dumps(task_data.get('task_config', {}))
        model = task_data['model']
        model_config = json.dumps(task_data.get('model_config', {}))
        status = TaskStatusEnum.CREATED

        task_info = TaskDAO.add(
            task_type=task_type,
            task_config=task_config,
            model=','.join(model),
            model_config=model_config,
            status=status,
        )
        return task_info.task_id

    @classmethod
    def get_total_task(cls, task_data):
        task_type = task_data.get('task_type')
        model = task_data.get('model')
        status = task_data.get('status')
        start_at_begin = task_data.get('start_at_begin')
        start_at_end = task_data.get('start_at_end')
        stop_at_begin = task_data.get('stop_at_begin')
        stop_at_end = task_data.get('stop_at_end')

        created_at_begin = task_data.get('created_at_begin')
        created_at_end = task_data.get('created_at_end')
        updated_at_begin = task_data.get('updated_at_begin')
        updated_at_end = task_data.get('updated_at_end')

        filters = []
        if task_type is not None:
            filters.append(TaskTab.task_type == task_type)
        if model is not None:
            filters.append(TaskTab.model == model)
        if status is not None:
            if isinstance(status, TaskStatusEnum):
                filters.append(TaskTab.status == status)
            elif isinstance(status, list):
                filters.append(TaskTab.status.in_(status))
        elif status is None:
            filters.append(TaskTab.status != TaskStatusEnum.DELETED)
        if start_at_begin is not None:
            filters.append(TaskTab.start_at >= start_at_begin)
        if start_at_end is not None:
            filters.append(TaskTab.start_at <= start_at_end)
        if stop_at_begin is not None:
            filters.append(TaskTab.stop_at >= stop_at_begin)
        if stop_at_end is not None:
            filters.append(TaskTab.stop_at <= stop_at_end)
        if created_at_begin is not None:
            filters.append(TaskTab.created_at >= created_at_begin)
        if created_at_end is not None:
            filters.append(TaskTab.created_at <= created_at_end)
        if updated_at_begin is not None:
            filters.append(TaskTab.updated_at >= updated_at_begin)
        if updated_at_end is not None:
            filters.append(TaskTab.updated_at <= updated_at_end)

        total = TaskDAO.count([and_(*filters)])
        return total

    @classmethod
    def update_task_by_filters(cls, filters, update_data):
        TaskDAO.update_by_filter_by(filters, update_data)

    @classmethod
    def update_task_by_id(cls, task_id, update_data):
        if 'model' in update_data:
            update_data['model'] = ','.join(update_data['model'])

        cls.update_task_by_filters({'task_id': task_id}, update_data)

    @classmethod
    def delete_task_by_id(cls, task_id):
        sub_task_list = SubTaskService.search_sub_task({'task_id': task_id, 'need_pagination': False})['list']
        sub_task_id_list = [info['sub_task_id'] for info in sub_task_list]
        if sub_task_id_list:
            SubTaskService.delete_sub_task_by_ids(sub_task_id_list)

        TaskDAO.update_by_filter_by({'task_id': task_id}, {'status': TaskStatusEnum.DELETED})


class SubTaskService(Service):
    @classmethod
    def search_sub_task(cls, sub_task_data):
        page_no = sub_task_data.get('page_no', 1)
        count = sub_task_data.get('count', 10)
        need_pagination = sub_task_data.get('need_pagination', True)

        task_id = sub_task_data.get('task_id')
        sub_task_id = sub_task_data.get('sub_task_id')
        serial_num = sub_task_data.get('serial_num')
        status = sub_task_data.get('status')
        start_at_begin = sub_task_data.get('start_at_begin')
        start_at_end = sub_task_data.get('start_at_end')
        stop_at_begin = sub_task_data.get('stop_at_begin')
        stop_at_end = sub_task_data.get('stop_at_end')

        created_at_begin = sub_task_data.get('created_at_begin')
        created_at_end = sub_task_data.get('created_at_end')
        updated_at_begin = sub_task_data.get('updated_at_begin')
        updated_at_end = sub_task_data.get('updated_at_end')

        offset = (int(page_no) - 1) * int(count)

        filters = []
        if task_id is not None:
            filters.append(SubTaskTab.task_id == task_id)
        if sub_task_id is not None:
            filters.append(SubTaskTab.sub_task_id == sub_task_id)
        if serial_num is not None:
            filters.append(SubTaskTab.serial_num == serial_num)
        if status is not None:
            if isinstance(status, TaskStatusEnum):
                filters.append(SubTaskTab.status == status)
            elif isinstance(status, list):
                filters.append(SubTaskTab.status.in_(status))
        elif status is None:
            filters.append(SubTaskTab.status != TaskStatusEnum.DELETED)
        if start_at_begin is not None:
            filters.append(SubTaskTab.start_at >= start_at_begin)
        if start_at_end is not None:
            filters.append(SubTaskTab.start_at <= start_at_end)
        if stop_at_begin is not None:
            filters.append(SubTaskTab.stop_at >= stop_at_begin)
        if stop_at_end is not None:
            filters.append(SubTaskTab.stop_at <= stop_at_end)
        if created_at_begin is not None:
            filters.append(SubTaskTab.created_at >= created_at_begin)
        if created_at_end is not None:
            filters.append(SubTaskTab.created_at <= created_at_end)
        if updated_at_begin is not None:
            filters.append(SubTaskTab.updated_at >= updated_at_begin)
        if updated_at_end is not None:
            filters.append(SubTaskTab.updated_at <= updated_at_end)

        if need_pagination:
            task_list = SubTaskDAO.get_list(filters=[and_(*filters)], offset=offset, limit=count)
        else:
            task_list = SubTaskDAO.get_list(filters=[and_(*filters)])
        task_list = [model_to_dict(obj) for obj in task_list]
        return {
            'list': task_list,
            'page_no': page_no,
            'count': count,
        }

    @classmethod
    def get_sub_task_by_id(cls, sub_task_id):
        task_info = SubTaskDAO.get_list(filters=[and_(SubTaskTab.sub_task_id == sub_task_id,
                                                      SubTaskTab.status != TaskStatusEnum.DELETED)])
        if task_info.first():
            return model_to_dict(task_info.first())
        else:
            return {}

    @classmethod
    def get_sub_task_by_task_id(cls, task_id):
        task_list = SubTaskDAO.get_list(filters=[and_(SubTaskTab.task_id == task_id,
                                                      SubTaskTab.status != TaskStatusEnum.DELETED)])
        task_id_list = [obj.sub_task_id for obj in task_list]
        return task_id_list

    @classmethod
    def get_total_task(cls, sub_task_data):
        task_id = sub_task_data.get('task_id')
        sub_task_id = sub_task_data.get('sub_task_id')
        serial_num = sub_task_data.get('serial_num')
        status = sub_task_data.get('status')
        start_at_begin = sub_task_data.get('start_at_begin')
        start_at_end = sub_task_data.get('start_at_end')
        stop_at_begin = sub_task_data.get('stop_at_begin')
        stop_at_end = sub_task_data.get('stop_at_end')

        created_at_begin = sub_task_data.get('created_at_begin')
        created_at_end = sub_task_data.get('created_at_end')
        updated_at_begin = sub_task_data.get('updated_at_begin')
        updated_at_end = sub_task_data.get('updated_at_end')

        filters = []
        if task_id is not None:
            filters.append(SubTaskTab.task_id == task_id)
        if sub_task_id is not None:
            filters.append(SubTaskTab.sub_task_id == sub_task_id)
        if serial_num is not None:
            filters.append(SubTaskTab.serial_num == serial_num)
        if status is not None:
            if isinstance(status, TaskStatusEnum):
                filters.append(TaskTab.status == status)
            elif isinstance(status, list):
                filters.append(TaskTab.status.in_(status))
        elif status is None:
            filters.append(SubTaskTab.status != TaskStatusEnum.DELETED)
        if start_at_begin is not None:
            filters.append(SubTaskTab.start_at >= start_at_begin)
        if start_at_end is not None:
            filters.append(SubTaskTab.start_at <= start_at_end)
        if stop_at_begin is not None:
            filters.append(SubTaskTab.stop_at >= stop_at_begin)
        if stop_at_end is not None:
            filters.append(SubTaskTab.stop_at <= stop_at_end)
        if created_at_begin is not None:
            filters.append(SubTaskTab.created_at >= created_at_begin)
        if created_at_end is not None:
            filters.append(SubTaskTab.created_at <= created_at_end)
        if updated_at_begin is not None:
            filters.append(SubTaskTab.updated_at >= updated_at_begin)
        if updated_at_end is not None:
            filters.append(SubTaskTab.updated_at <= updated_at_end)

        total = SubTaskDAO.count([and_(*filters)])
        return total

    @classmethod
    def create_sub_task(cls, sub_task_data):
        sub_task_info = SubTaskDAO.add(**sub_task_data)
        return sub_task_info.sub_task_id

    @classmethod
    def delete_sub_task_by_ids(cls, sub_task_ids):
        SubTaskDAO.update_by_filter([and_(SubTaskTab.sub_task_id.in_(sub_task_ids))], {'status': TaskStatusEnum.DELETED})

    @classmethod
    def update_sub_task_by_filters(cls, filters, update_data):
        SubTaskDAO.update_by_filter_by(filters, update_data)

    @classmethod
    def update_sub_task_by_id(cls, sub_task_id, update_data):
        sub_task_info = cls.get_sub_task_by_id(sub_task_id)
        if sub_task_info and sub_task_info['status'] == 'DONE' and 'status' in update_data:
            update_data.pop('status')
        cls.update_sub_task_by_filters({'sub_task_id': sub_task_id}, update_data)
