import datetime
import json

from src.dms.scheduler.base import scheduler
from src.dms.config.enums import TaskStatusEnum
from src.dms.services.task import TaskService, SubTaskService


def _calculate_task_status_and_progress(task_id):
    from src.dms.app import _app
    _app.logger.info(f'begin _calculate_task_status_and_progress|task_id: {task_id}')
    sub_task_list = SubTaskService.search_sub_task({'task_id': task_id})
    sub_task_list = sub_task_list['list']
    sub_task_status_list = [obj['status'] for obj in sub_task_list]
    sub_task_status_list = list(set(sub_task_status_list))
    if len(sub_task_status_list) == 1 and TaskStatusEnum.PENDING in sub_task_status_list:
        return TaskStatusEnum.PENDING, {}
    total = 0
    count = 0
    for sub_task in sub_task_list:
        sub_task_progress = json.loads(sub_task['progress'])
        total += sub_task_progress.get('total', 0)
        count += sub_task_progress.get('count', 0)
    if len(sub_task_status_list) == 1:
        return sub_task_status_list[0], {'total': total, 'count': count}
    if TaskStatusEnum.RUNNING in sub_task_status_list:
        return TaskStatusEnum.RUNNING, {'total': total, 'count': count}
    if len(sub_task_status_list) > 1 and TaskStatusEnum.PENDING in sub_task_status_list:
        return TaskStatusEnum.RUNNING, {'total': total, 'count': count}
    if len(sub_task_status_list) > 1 and TaskStatusEnum.FAILED in sub_task_status_list:
        return TaskStatusEnum.FAILED, {'total': total, 'count': count}


@scheduler.task('interval', id='do_sync_task_status', seconds=120)
def sync_task_status():
    """
    Synchronize task status information, including status and progress
    :return:
    """
    SYNC_TASK_PERIOD_SECONDS = 130  # The time needs to be slightly longer than the scheduled task running time
    from src.dms.app import _app
    _app.logger.info(f'Begin do_sync_task_status job at {datetime.datetime.now()}')
    with _app.app_context():
        updated_at_begin = (datetime.datetime.now() + datetime.timedelta(seconds=-SYNC_TASK_PERIOD_SECONDS)
                            ).strftime("%Y-%m-%d %H:%M:%S")
        pending_sync_sub_task_list = SubTaskService.search_sub_task({'updated_at_begin': updated_at_begin,
                                                                     'need_pagination': False})
        pending_sync_sub_task_list = pending_sync_sub_task_list['list']
        task_id_list = [sub_task['task_id'] for sub_task in pending_sync_sub_task_list]
        task_id_list = list(set(task_id_list))
        for task_id in task_id_list:
            task_status, progress = _calculate_task_status_and_progress(task_id)
            TaskService.update_task_by_id(task_id, {'status': task_status, 'progress': progress})
            _app.logger.info(f'end _calculate_task_status_and_progress|task_id: {task_id}, '
                             f'status: {task_status}, progress: {progress}')
    _app.logger.info(f'End do_sync_task_status job at {datetime.datetime.now()}')
