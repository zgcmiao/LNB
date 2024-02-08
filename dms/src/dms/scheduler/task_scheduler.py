import datetime
import json
import math
import os.path

from src.dms.scheduler.base import scheduler
from src.dms.config import constant
from src.dms.config.enums import TaskStatusEnum
from src.dms.services.task import TaskService, SubTaskService
from src.dms.utils.question_utils import get_questions_from_exam_file_path


def _get_exam_file_path_from_subject(subject, subject_absolute_dir, data_absolute_root):
    with open(os.path.join(subject_absolute_dir, f'{subject}.json'), encoding='utf-8') as f:
        data = json.load(f)
        list_exam_file_path = data[constant.SUBJECT_EXAM_FILE]
    list_exam_file_path = [os.path.join(data_absolute_root, file_path) for file_path in list_exam_file_path]
    return list_exam_file_path


def _get_model_path(model_name):
    return 'models--{}'.format(model_name.replace('/', '--'))


def _gen_command(model_name, task_id, index, list_subject, list_shot_type,
                 llm_bench_docker_version=constant.DEFAULT_LLM_BENCH_DOCKER_VERSION,
                 llm_bench_version=constant.DEFAULT_LLM_BENCH_VERSION, cot=False, rag=False):
    nfs_path = os.getenv('NFS_PATH')
    model_path = _get_model_path(model_name)
    command = constant.COMMAND_FORMAT.format(model_path=model_path, model_name=model_name,
                                             list_subject=' '.join(list_subject),
                                             list_shot_type=' '.join(list_shot_type),
                                             llm_bench_docker_version=llm_bench_docker_version,
                                             llm_bench_version=llm_bench_version,
                                             nfs_path=nfs_path,
                                             )
    if cot:
        command += ' --cot'
    if rag:
        command += ' --rag'
    return command


def _save_sub_task(task_id, task_config, model_config, list_subject, list_shot_type, model, index):
    sub_task_config = task_config
    sub_task_config[constant.TASK_LIST_SUBJECT] = list_subject
    sub_task_config[constant.TASK_LIST_SHOT_TYPE] = list_shot_type
    sub_task_config[constant.TASK_LIST_MODEL] = [model]
    llm_bench_docker_version = sub_task_config.get(constant.TASK_LLM_BENCH_DOCKER_VERSION,
                                                   constant.DEFAULT_LLM_BENCH_DOCKER_VERSION)
    llm_bench_version = sub_task_config.get(constant.TASK_LLM_BENCH_VERSION, constant.DEFAULT_LLM_BENCH_VERSION)
    cot = sub_task_config.get(constant.TASK_COT_PARAM, False)
    rag = sub_task_config.get(constant.TASK_RAG_PARAM, False)

    command = _gen_command(model, task_id, index, list_subject, list_shot_type, llm_bench_docker_version,
                           llm_bench_version, cot=cot, rag=rag)

    sub_task_data = {
        'task_id': task_id,
        'sub_task_config': json.dumps(sub_task_config),
        'command': command,
        'model': model,
        'model_size': model_config.get(model, {}).get('model_size'),
        'serial_num': '',
        'output_file_path': '',
        'output_result': '{}',
        'status': TaskStatusEnum.PENDING,
        'progress': '{}'
    }
    return SubTaskService.create_sub_task(sub_task_data)


def _split_task(task_id, split_batches, subject, subject_absolute_dir, data_absolute_root, breakpoint_file,
                prefer_subject_prefix=None, cot=False):
    from src.dms.app import _app
    if subject:
        list_exam_file_path = _get_exam_file_path_from_subject(subject, subject_absolute_dir, data_absolute_root)
        _app.logger.info(f'split task, list_exam_file_path: {list_exam_file_path}')
        list_questions = get_questions_from_exam_file_path(list_exam_file_path, breakpoint_file)
        _app.logger.info(f'split task, list_questions length: {len(list_questions)}')
    else:
        list_questions = get_questions_from_exam_file_path([data_absolute_root], breakpoint_file)
    if not split_batches:
        split_batches = len(list_questions)

    nfs_path = os.getenv('NFS_PATH')
    sub_task_data_dir = os.path.join(constant.RESULT_FILE_PATH.format(nfs_path=nfs_path, task_id=task_id),
                                     constant.DATA_SOURCE_DIR, task_id)
    os.makedirs(sub_task_data_dir, exist_ok=True)
    sub_task_subject_dir = os.path.join(constant.RESULT_FILE_PATH.format(nfs_path=nfs_path, task_id=task_id),
                                        constant.SUBJECT_DIR)
    os.makedirs(sub_task_subject_dir, exist_ok=True)

    if subject:
        with open(os.path.join(subject_absolute_dir, f'{subject}.json'), encoding='utf-8') as f:
            subject_data = json.load(f)
    elif cot:
        subject_data = constant.DEFAULT_COT_SUBJECT_DATA
    else:
        subject_data = constant.DEFAULT_SUBJECT_DATA

    subject_file_mapping = {}
    question_length = len(list_questions)
    for i in range(math.ceil(question_length / split_batches)):
        low_index = i * split_batches
        high_index = min(low_index + split_batches, question_length)
        part_questions = list_questions[low_index: high_index]
        part_file_name = constant.SUB_TASK_FILE_NAME_FORMAT.format(task_id=task_id, index=i)
        part_file_path = os.path.join(sub_task_data_dir, f'{part_file_name}.json')

        if subject:
            part_id = subject
        elif prefer_subject_prefix:
            part_id = prefer_subject_prefix
        else:
            part_id = constant.SUB_TASK_ID_FORMAT.format(subject='default', task_id=task_id, index=i)
        with open(part_file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'id': part_id,
                'title': '',
                'questions': part_questions
            }, f, indent=4, ensure_ascii=False)

        subject_data[constant.SUBJECT_EXAM_FILE] = [os.path.join(constant.DATA_SOURCE_DIR, task_id,
                                                                 f'{part_file_name}.json')]
        part_subject_file_name = constant.SUB_TASK_SUBJECT_FILE_NAME_FORMAT.format(
            subject=subject or prefer_subject_prefix or 'default', task_id=task_id, index=i)
        with open(os.path.join(sub_task_subject_dir, f'{part_subject_file_name}.json'), 'w', encoding='utf-8') as f:
            json.dump(subject_data, f, indent=4, ensure_ascii=False)
        subject_file_mapping[part_subject_file_name] = {
            constant.TASK_SUBJECT_ABSOLUTE_FILE_PATH: os.path.join(sub_task_subject_dir,
                                                                   f'{part_subject_file_name}.json'),
            constant.TASK_DATA_ABSOLUTE_FILE_PATH: part_file_path,
        }
        _app.logger.info(f'split task, index: {i}, part_file_path: {part_file_path}, '
                         f'part_subject_file_name: {part_subject_file_name}')

    return subject_file_mapping


def _gen_sub_task(task_data: dict):
    from src.dms.app import _app
    try:
        task_config = json.loads(task_data['task_config'])
    except Exception as e:
        _app.logger.error(f'error in convert task_config str to json, exception: {repr(e)}, '
                          f'task_config: {task_data["task_config"]}')
        raise e

    try:
        model_config = json.loads(task_data['model_config'])
    except Exception as e:
        _app.logger.error(f'error in convert model_config str to json, exception: {repr(e)}, '
                          f'task_config: {task_data["model_config"]}')
        raise e
    task_id = task_data['task_id']
    _app.logger.info(f'begin split task: {task_id}')

    list_subject = task_config.get(constant.TASK_LIST_SUBJECT)
    list_shot_type = task_config.get(constant.TASK_LIST_SHOT_TYPE, constant.DEFAULT_SHOT_TYPES)
    list_model = task_data['model'].split(',') if task_data['model'] else ''
    prefer_subject_prefix = task_config.get(constant.TASK_PREFER_SUBJECT_PREFIX)
    cot = task_config.get(constant.TASK_COT_PARAM, False)

    split_batches = task_config.get(constant.TASK_SPLIT_BATCHES)
    subject_absolute_dir = task_config.get(constant.TASK_SUBJECT_ABSOLUTE_DIR)
    data_absolute_root = task_config[constant.TASK_DATA_ABSOLUTE_ROOT]
    breakpoint_file = task_config.get(constant.TASK_BREAKPOINT_FILE_PARAM, '')

    for model in list_model:
        for shot_type in list_shot_type:
            sub_subject_file_mapping = {}
            if not list_subject:
                sub_subject_file_mapping = _split_task(task_id, split_batches, None, None, data_absolute_root,
                                                       breakpoint_file, prefer_subject_prefix, cot=cot)
            else:
                for subject in list_subject:
                    try:
                        tmp_mapping = _split_task(task_id, split_batches, subject, subject_absolute_dir,
                                                  data_absolute_root, breakpoint_file, cot=cot)
                        sub_subject_file_mapping.update(**tmp_mapping)
                    except Exception as e:
                        _app.logger.error(f'Error in split task. task_id: {task_id}, error: {repr(e)}')
                        raise e
            index = 0
            for sub_subject, file_path_dict in sub_subject_file_mapping.items():
                task_config[constant.TASK_SUBJECT_ABSOLUTE_FILE_PATH] = file_path_dict.get(
                    constant.TASK_SUBJECT_ABSOLUTE_FILE_PATH, '')
                task_config[constant.TASK_DATA_ABSOLUTE_FILE_PATH] = file_path_dict.get(
                    constant.TASK_DATA_ABSOLUTE_FILE_PATH, '')
                _save_sub_task(task_id, task_config, model_config, [sub_subject], [shot_type], model, index)
                index += 1


@scheduler.task('interval', id='do_split_main_task', seconds=12)
def split_main_task():
    """
    Scan task_tab regularly, split the tasks that need to be split, and save them to sub_task_tab.
    Status changes in task_tab: Created -> Pending
    The status of the newly created sub_task in sub_task_tab: Pending
    :return:
    """
    from src.dms.app import _app
    _app.logger.info(f'Begin do_split_main_task at {datetime.datetime.now()}')
    with _app.app_context():
        created_task_list = TaskService.search_task_list({'status': TaskStatusEnum.CREATED, 'need_pagination': False})
        created_task_list = created_task_list['list']
        for task_obj in created_task_list:
            TaskService.update_task_by_id(task_obj['task_id'], {'status': TaskStatusEnum.PENDING})
            try:
                _gen_sub_task(task_obj)
            except Exception as e:
                print('error! exception: {}'.format(repr(e)))
                TaskService.update_task_by_id(task_obj['task_id'], {'status': TaskStatusEnum.CREATED})
    _app.logger.info(f'End do_split_main_task at {datetime.datetime.now()}')
