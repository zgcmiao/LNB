from flask import Blueprint, request

from src.dms.json_schema import task_schemas
from src.dms.apis.base import catch_error
from src.dms.services.task import TaskService, SubTaskService
from src.dms.utils.log_utils import log_request
from src.dms.utils.request_utils import response_data, parse_params

api = Blueprint('task', __name__)


@api.get('/list')
@log_request(False)
@parse_params(
    task_schemas.SEARCH_TASK_SCHEMA, method='GET'
)
@catch_error
def search_task(data):
    result = TaskService.search_task_list(data)
    return response_data(result)


@api.get('/detail')
@log_request(False)
@parse_params(
    task_schemas.GET_TASK_SCHEMA, method='GET'
)
@catch_error
def get_task(data):
    task_id = data['task_id']
    task_info = TaskService.get_task_by_id(task_id)
    return response_data(task_info)


@api.get('/total')
@log_request(False)
@parse_params(task_schemas.GET_TOTAL_COUNT_SCHEMA, method='GET')
@catch_error
def get_total_task(data):
    total = TaskService.get_total_task(data)
    return response_data({'total': total})


@api.post('/create')
@log_request()
@parse_params(task_schemas.CREATE_TASK_SCHEMA, method='POST', data_format='JSON')
@catch_error
def create_task(data):
    task_id = TaskService.create_task(data)
    return response_data({'task_id': task_id})


@api.post('/update')
@log_request()
@parse_params(task_schemas.UPDATE_TASK_SCHEMA, method='POST', data_format='JSON')
@catch_error
def update_task(data):
    task_id = data['task_id']
    TaskService.update_task_by_id(task_id, data)
    return response_data()


@api.post('/delete')
@log_request()
@parse_params(task_schemas.DELETE_TASK_SCHEMA, method='POST', data_format='JSON')
@catch_error
def delete_task(data):
    task_id = data['task_id']
    TaskService.delete_task_by_id(task_id)
    return response_data()


@api.get('/sub_task/list')
@log_request(False)
@parse_params(task_schemas.SEARCH_SUB_TASK_SCHEMA, method='GET')
@catch_error
def search_sub_task(data):
    result = SubTaskService.search_sub_task(data)
    return response_data(result)


@api.get('/sub_task/detail')
@log_request(False)
@parse_params(task_schemas.GET_SUB_TASK_SCHEMA, method='GET')
@catch_error
def get_sub_task(data):
    sub_task_id = data['sub_task_id']
    task_info = SubTaskService.get_sub_task_by_id(sub_task_id)
    return response_data(task_info)


@api.get('/sub_task/total')
@log_request(False)
@parse_params(task_schemas.GET_TOTAL_SUB_TASK_SCHEMA, method='GET')
@catch_error
def get_total_sub_task(data):
    total = SubTaskService.get_total_task(data)
    return response_data({'total': total})


@api.post('/sub_task/update')
@log_request()
@parse_params(task_schemas.UPDATE_SUB_TASK_SCHEMA, method='POST', data_format='JSON')
@catch_error
def update_sub_task(data):
    sub_task_id = data['sub_task_id']
    SubTaskService.update_sub_task_by_id(sub_task_id, data)
    return response_data()
