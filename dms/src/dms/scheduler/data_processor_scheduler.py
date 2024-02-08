import datetime
import json
import math
import os.path
import re
import string

from src.dms.scheduler.base import scheduler, get_opensearch_client
from src.dms.config import constant
from src.dms.config.enums import TaskStatusEnum, QuestionType
from src.dms.services.task import SubTaskService
from src.dms.utils.question_utils import get_answer, get_questions_from_exam_file_path


def _save_results_to_opensearch(result_list):
    from src.dms.app import _app
    opensearch_client = get_opensearch_client()

    _app.logger.info(f'_save_results_to_opensearch | begin save result. result_list len: {len(result_list)}')
    result_index = 'inference_result_index'
    if not opensearch_client.indices.exists(result_index):
        _app.logger.info(f'_save_results_to_opensearch | opensearch_client index not exists, will create {result_index}')
        opensearch_client.indices.create(
            result_index, body={
                'settings': {
                    'index': {
                        'number_of_shards': 4
                    }
                }
            }
        )
    batch_size = 1000
    _app.logger.info(f'_save_results_to_opensearch | begin save result to index:{result_index}')
    for i in range(math.ceil(len(result_list)/batch_size)):
        low = i * batch_size
        high = min(low + batch_size, len(result_list))
        tmp_result = result_list[low: high]
        body = ''
        for r in tmp_result:
            if body:
                body += '\n'
            body += json.dumps({"index": {"_index": result_index}}) + '\n' + json.dumps(r)
        opensearch_client.bulk(body, refresh=True)
    opensearch_client.close()
    _app.logger.info(f'_save_results_to_opensearch | end save result.')


def _question_key(id, title):
    return f"{id}_{title}"


def _raw_answer_parsing(raw_answer, exam_id=None, cot=False, question_type=QuestionType.MULTIPLE_CHOICE):
    id = ''
    if raw_answer.get("id"):
        id = raw_answer.get("id")
    elif exam_id:
        id = exam_id

    ans = raw_answer.get("answer")
    if question_type in [QuestionType.MULTIPLE_CHOICE]:
        if ans.startswith('The following are multiple choice questions'):
            matches = re.findall(r'Answer: ([A-Z])', ans)
            ans = matches[-1] if matches else ''
        else:
            ans = ans.splitlines()[0].strip() if ans else ''
            if ans != '' and ans not in string.ascii_uppercase:
                ans = get_answer(raw_answer.get("answer").strip(), cot)
                ans = ''.join(ans)
            elif ans == '':
                ans = get_answer(raw_answer.get("answer").strip(), cot)
                ans = ''.join(ans)
    elif question_type in [QuestionType.CLOZE]:
        ans = ans.splitlines()[0].strip() if ans else ''
    elif question_type in [QuestionType.QUESTION_AND_ANSWER]:
        ans = ans.splitlines()[0].strip() if ans else ''
    return id, raw_answer.get("title"), ans


def _summarize_sub_task_by_output_file(task_id, task_config, output_file_path):
    from src.dms.app import _app
    _app.logger.info(f'begin _summarize_sub_task_by_output_file | task_id:{task_id}, task_config:{task_config},'
                     f' output_file_path:{output_file_path}.')
    try:
        task_config = json.loads(task_config)
    except Exception as e:
        _app.logger.error(f'error in covert task_config to json, exception: {repr(e)}, task_config: {task_config}')
        return
    data_absolute_file_path = task_config.get(constant.TASK_DATA_ABSOLUTE_FILE_PATH)
    question_type = task_config.get(constant.TASK_QUESTION_TYPE)

    if not data_absolute_file_path or not os.path.isfile(data_absolute_file_path):
        _app.logger.error(f'source file {data_absolute_file_path} is not exists, will skip. task_id:{task_id}.')
        return
    if not os.path.isfile(output_file_path):
        _app.logger.error(f'output file {output_file_path} is not exists, will skip. task_id: {task_id}.')
        return

    list_questions = get_questions_from_exam_file_path([data_absolute_file_path])
    _app.logger.info(f'_summarize_sub_task_by_output_file | task_id:{task_id}, list_questions len:{len(list_questions)}')
    result_mapping = {}
    for q in list_questions:
        key = _question_key(q['exam_id'], q['title'])
        if 'choice' in q['answer']:
            ans = q['answer']['choice']
        else:
            ans = q['answer']
        result_mapping[key] = {'question': q, 'answer': ans}

    list_answer = []
    with open(output_file_path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                line_dict = eval(line.replace('\n', '').strip())
                list_answer.append(line_dict)
            except Exception as ex:
                _app.logger.error(f'error in covert. exception: {ex}, line: {line}')
                continue
    _app.logger.info(f'_summarize_sub_task_by_output_file | task_id:{task_id}, list_answer len:{len(list_answer)}')
    result_list = []
    for answer in list_answer:
        exam_id, title, answer_parsed = _raw_answer_parsing(answer, question_type=question_type)
        question_dict = result_mapping.get(_question_key(exam_id, title), {})
        question_choice_str = ''
        for choice in question_dict.get('question', {}).get('choices', []):
            question_choice_str += f'{choice["name"] or ""}. {choice["content"] or ""} '

        result_list.append(
            {
                'exam_id': exam_id,
                'title': title,
                'result': answer_parsed,
                'predict': answer.get('predict', ''),
                'correct': question_dict.get('answer', ''),
                'sub_task_id': task_id,
                'question_content': question_dict.get('question', {}).get('content'),
                'question_choice_str': question_choice_str,
            }
        )
    # _save_results(result_list)
    _save_results_to_opensearch(result_list)
    _app.logger.info(f'Success in _summarize_sub_task_by_output_file | task_id:{task_id}, task_config:{task_config},'
                     f' output_file_path:{output_file_path}.')


@scheduler.task('interval', id='do_save_task_result', seconds=60*30)
def save_task_result():
    """
    Summarize the evaluation task running results. Summarize results from result file into opensearch
    For the subtask that has summarized the results, update the status to Done
    :return:
    """
    from src.dms.app import _app
    _app.logger.info(f'Begin do_save_task_result job at {datetime.datetime.now()}')
    with _app.app_context():
        pending_summarized_sub_task = SubTaskService.search_sub_task({'status': [TaskStatusEnum.SUCCESS],
                                                                      'need_pagination': False})
        pending_summarized_sub_task = pending_summarized_sub_task['list']
        for sub_task in pending_summarized_sub_task:
            if sub_task['output_file_path'] == '':
                _app.logger.info(f'sub task {sub_task["sub_task_id"]} has no output_file, will skip...')
                _app.logger.info(f'_summarize_sub_task_by_output_file end, will update sub_task status.'
                                 f' sub_task_id:{sub_task["sub_task_id"]}.')
                SubTaskService.update_sub_task_by_id(sub_task['sub_task_id'], {'status': TaskStatusEnum.DONE})
                continue
            _summarize_sub_task_by_output_file(sub_task['sub_task_id'], sub_task['sub_task_config'],
                                               sub_task['output_file_path'])
            _app.logger.info(f'_summarize_sub_task_by_output_file end, will update sub_task status.'
                             f' sub_task_id:{sub_task["sub_task_id"]}.')
            SubTaskService.update_sub_task_by_id(sub_task['sub_task_id'], {'status': TaskStatusEnum.DONE})
    _app.logger.info(f'End do_save_task_result job at {datetime.datetime.now()}')
