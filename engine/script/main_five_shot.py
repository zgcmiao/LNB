# -*- coding: utf-8 -*-
import argparse
import json
import os
import tempfile
from pathlib import Path

from conf import QuestionType, LanguageType, get_enum_item_by_value, MetricName, Conf, ModelType
from data import DataManager
from evaluation_pipeline import PipelineManager
from script import detect_model_type, filter_question, format_question, QuestionPromptStrategy
from script.helper.prompt_helper import question_format_convert_handler
from script.helper.script_helper import get_default_metric
from utils import CommonHelper

FIVE_SHOT_FILE_FORMAT = '%s.auto.%s-five-shot.json'
DEFAULT_SHOT_TYPE = "five-shot"


def _list_example_item_by_subject(subject_cfg, subject_example_keys):
    subject_example_questions = []
    list_example_file_path = [f'{_}' for _ in subject_cfg['example_files']]
    list_example_file_path = DataManager().get_data_file_path(list_example_file_path)

    for example_path in list_example_file_path:
        with open(example_path) as f_in:
            exam_data = json.load(f_in)
            exam_id = exam_data['id']
            questions = exam_data['questions']
            for q in filter(filter_question, questions):
                q['exam_id'] = exam_id
                q_key = (exam_id, q['title'])
                if q_key in subject_example_keys:
                    subject_example_questions.append(q)
    return subject_example_questions


def _list_exam_item_by_subject(subject_cfg, data_dir, subject_example_keys, breakpoint_file=None):
    list_exam_file_path = []
    subject_test_questions = []
    continue_key = None
    if breakpoint_file and os.path.isfile(breakpoint_file):
        with open(breakpoint_file) as f:
            lines = f.readlines()
            last_line = lines[-1].replace('\n', '')
            last_question = json.loads(last_line)
            continue_key = f'{last_question["id"]}_{last_question["title"]}'

    # data_dir is not None
    # list exam from data_dir
    if data_dir is not None:
        if isinstance(data_dir, str):
            list_exam_file_path.append(data_dir)
        else:
            list_exam_file_path += data_dir
    # data_dir is None
    # list exam from subject_cfg['exam_files']
    else:
        list_exam_file_path = [f'{_}' for _ in subject_cfg['exam_files']]
        list_exam_file_path = DataManager().get_data_file_path(list_exam_file_path)

    find_breakpoint_flag = False
    for exam_path in list_exam_file_path:
        with open(exam_path) as f_in:
            exam_data = json.load(f_in)
            exam_id = exam_data['id']
            questions = exam_data['questions']
            for q in filter(filter_question, questions):
                q['exam_id'] = exam_id
                q_key = (exam_id, q['title'])
                if q_key not in subject_example_keys:
                    if continue_key and not find_breakpoint_flag:
                        if f'{exam_id}_{q["title"]}' == continue_key:
                            find_breakpoint_flag = True
                        else:
                            continue
                    else:
                        subject_test_questions.append(q)

    return subject_test_questions


def _get_cfg_by_subject(subject):
    with open(DataManager().get_data_file_path(f'metadata/subjects/{subject}.json')) as f_cfg:
        subject_cfg = json.load(f_cfg)
    return subject_cfg


def _get_output_name(model_name, finetune_weights):
    if finetune_weights:
        if Path(finetune_weights).is_dir():
            output_model_name = Path(finetune_weights).name.replace('/', '-')
        else:
            output_model_name = finetune_weights.replace('/', '-')
    else:
        output_model_name = model_name.replace('/', '-')
    return output_model_name


def run(model_name: str, version: str, model_type: ModelType, subject, data_dir=None, output_dir=None, *args, **kwargs):
    """ run five-shot

    :param model_name: model name
    :param version: version
    :param model_type: model type
    :param subject: subject
    :param data_dir: data dir
    :param output_dir: output dir
    :param args: args dir
    :param kwargs: kwargs
    """
    cot = kwargs.get('cot')
    rag = kwargs.get('rag')
    dry_run = kwargs.get("dry_run")
    pipeline_id = kwargs.get("pipeline_id")
    finetune_weights = kwargs.get("finetune_weights")
    need_merge_weights = kwargs.get("need_merge_weights")
    language_type = kwargs.get("language_type") or LanguageType.EN
    question_type = kwargs.get("question_type") or QuestionType.MULTIPLE_CHOICE
    metric_name = kwargs.get("metric_name") or get_default_metric(question_type)
    breakpoint_file = kwargs.get("breakpoint_file")
    # json_dynamic_params = kwargs.get("json_dynamic_params") or {}
    # First generate the explanation and then the reasoning, must be a cot case
    pre_gen_explanation_for_inference = kwargs.get("pre_gen_explanation_for_inference") if cot else False
    customized_model_package = kwargs.get("customized_model_package") or ""

    subject_cfg = _get_cfg_by_subject(subject)
    subject_example_keys = set((e['exam_id'], e['question_id']) for e in subject_cfg['examples'])
    list_subject_example_questions = _list_example_item_by_subject(subject_cfg, subject_example_keys)
    list_subject_test_questions = _list_exam_item_by_subject(subject_cfg, data_dir, subject_example_keys, breakpoint_file)

    prompt_header_parts = [QuestionPromptStrategy(question_type).generate_prompt_header(
        **{"subject_name": subject_cfg["name"],
           "subject_zh_name": subject_cfg.get("zh_name", subject_cfg["name"]),
           "target_language": language_type})]

    for q in list_subject_example_questions:
        base_inputs = {"cot": cot, "rag": rag, "with_answer": True, "target_language": language_type}
        # example is multiple_choice type need convert to specified `question_type`
        dict_inputs = question_format_convert_handler(raw_question_type=QuestionType.MULTIPLE_CHOICE,
                                                      target_question_type=question_type,
                                                      raw_question=q, **base_inputs)
        prompt_header_parts.append(format_question(q, question_type, dict_inputs=dict_inputs, **base_inputs))

    prompt_header = '\n\n'.join(prompt_header_parts)

    def _prompt_func(**kwargs):
        if kwargs.get("item_content", False):
            question_item_content = kwargs['item_content']
            return prompt_header + '\n\n' + format_question(question_item_content, question_type, **{"cot": cot,
                                                                                                     "rag": rag,
                                                                                                     "with_answer": False,
                                                                                                     "target_language": language_type})
        else:
            return prompt_header + '\n\n'

    _cot_no_explanation_prompt_generator_func = None
    if pre_gen_explanation_for_inference:
        # Only when you need to use the cot method and generate an explanation in advance
        # cot is all passed to False because the explanation has been pre-generated
        def _cot_no_explanation_prompt_generator_func(**kwargs):
            if kwargs.get("item_content", False):
                question_item_content = kwargs['item_content']
                return prompt_header + '\n\n' + format_question(question_item_content, question_type, **{"cot": False,
                                                                                                         "rag": rag,
                                                                                                         "with_answer": False,
                                                                                                         "target_language": language_type})
            else:
                return prompt_header + '\n\n'

    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = os.path.join(tmpdir, FIVE_SHOT_FILE_FORMAT % (pipeline_id, subject))
        with open(data_path, 'w') as f_out:
            json.dump(dict(id=subject, title=subject, questions=list_subject_test_questions), f_out)

            input_file_or_directory_path = data_path
            output_directory_path = f"{output_dir}/model/{_get_output_name(model_name, finetune_weights)}/"
            if not os.path.exists(output_directory_path):
                os.makedirs(output_directory_path)

        # TODO: convert get model inference params from configure yaml
        pipeline_instance = PipelineManager(version).get_pipeline_instance(model_name,
                                                                           model_type,
                                                                           pipeline_params={
                                                                               "name": model_name,
                                                                               "subject": subject,
                                                                               "shot_type": DEFAULT_SHOT_TYPE,
                                                                               "input_file_or_directory_path": input_file_or_directory_path,
                                                                               "output_directory_path": output_directory_path,
                                                                               "prompt_generator_func": _prompt_func,
                                                                               "dry_run": dry_run,
                                                                               "pipeline_id": pipeline_id,
                                                                               "question_type": question_type,
                                                                               "metric_name": metric_name,
                                                                               "pre_gen_explanation_for_inference": pre_gen_explanation_for_inference,
                                                                               "cot_no_explanation_prompt_generator_func": _cot_no_explanation_prompt_generator_func,
                                                                           },
                                                                           model_params={
                                                                               "finetune_weights": finetune_weights,
                                                                               "need_merge_weights": need_merge_weights,
                                                                               "customized_model_package": customized_model_package,
                                                                           }
                                                                           )
        pipeline_instance.run_step_by_processes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name_or_path')
    parser.add_argument('subject')
    # Need to specify a model category in the `ModelType` enum. e.g.: llama、falcon...
    parser.add_argument('model_type')
    parser.add_argument('--version', default=Conf.DEFAULT_VERSION)
    parser.add_argument('--data_dir', default=None)
    parser.add_argument('--output_dir', default='output')
    parser.add_argument('--cot', action=argparse.BooleanOptionalAction)
    parser.add_argument('--rag', action=argparse.BooleanOptionalAction)
    parser.add_argument('--dry_run', action=argparse.BooleanOptionalAction)
    parser.add_argument('--pipeline_id', default=None)
    # parser.add_argument('--batch_size', type=int)
    # parser.add_argument('--device')
    # parser.add_argument('--device_map')
    # parser.add_argument('--max_new_tokens', type=int, default=10)
    parser.add_argument("--finetune_weights", default=None)
    parser.add_argument("--need_merge_weights", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--language_type', choices=[v.value for v in LanguageType], default=LanguageType.EN.value)
    parser.add_argument("--question_type", choices=[v.value for v in QuestionType],
                        default=QuestionType.MULTIPLE_CHOICE.value)
    parser.add_argument("--metric_name", choices=[v.value for v in MetricName], help='the metric name')
    parser.add_argument("--breakpoint_file", default=None, help='the breakpoint file path')
    parser.add_argument("--json_dynamic_params", default=None, help='pass the params by json str')
    parser.add_argument('--pre_gen_explanation_for_inference', action=argparse.BooleanOptionalAction)
    parser.add_argument("--customized_model_package", default='', help="the customized model package path")

    args = parser.parse_args()
    model_name_or_path = args.model_name_or_path
    subject = args.subject
    model_type = detect_model_type(args.model_type)
    data_dir = args.data_dir
    output_dir = args.output_dir
    # batch_size = args.batch_size
    dry_run = args.dry_run or False
    pipeline_id = args.pipeline_id if args.pipeline_id else str(CommonHelper.generate_uuid())
    cot = args.cot or False
    rag = args.rag or False
    finetune_weights = args.finetune_weights
    need_merge_weights = args.need_merge_weights
    language_type = get_enum_item_by_value(LanguageType, args.language_type)
    question_type = get_enum_item_by_value(QuestionType, args.question_type)
    metric_name = get_enum_item_by_value(MetricName, args.metric_name)
    breakpoint_file = args.breakpoint_file
    json_dynamic_params = args.json_dynamic_params
    version = args.version
    pre_gen_explanation_for_inference = args.pre_gen_explanation_for_inference or False
    customized_model_package = args.customized_model_package

    if model_type == ModelType.CUSTOMIZED:
        assert customized_model_package, "Customized model need --customized_model_package argument."

    assert '..' not in model_name_or_path
    if json_dynamic_params:
        try:
            json_dynamic_params = json.loads(json_dynamic_params)
        except:
            raise ValueError("param `json_dynamic_params` should be a json str.")

    run(model_name_or_path, version, model_type, subject, data_dir, output_dir,
        **{"dry_run": dry_run, "pipeline_id": pipeline_id, "cot": cot, "rag": rag, "finetune_weights": finetune_weights,
           "need_merge_weights": need_merge_weights, "language_type": language_type, "question_type": question_type,
           "metric_name": metric_name, "breakpoint_file": breakpoint_file, "json_dynamic_params": json_dynamic_params,
           "pre_gen_explanation_for_inference": pre_gen_explanation_for_inference,
           "customized_model_package": customized_model_package})


if __name__ == "__main__":
    import time

    begin_time = time.time()
    main()
    end_time = time.time()
