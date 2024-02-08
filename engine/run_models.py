# -*- coding: utf-8 -*-
import argparse as argparse
import os
import time

from conf import Conf, error_code, QuestionType, LanguageType, get_enum_item_by_value, MetricName, ModelType
from script import get_default_metric, read_sys_env, run_get_result, MODEL_DICT_MAPPER
from utils import task_logger, CommonHelper

CONFIGURE_TRANSLATION = "network_configure_translation"

os.system(f"export PYTHONPATH=$PYTHONPATH:{os.getcwd()}")


def _pre_check_env():
    """ pre check env

    """
    if not CommonHelper.check_python_interpreter(Conf.PYTHON_INTERPRETER_PATH):
        raise error_code.ParameterError(
            "Invalid interpreter specified. Please adjust `Conf.PYTHON_INTERPRETER` parameter.")


def _run_gpt_script(data_path, api_key, model_name, pipeline_id, output_dir='output'):
    """ run gpt script """
    output_directory_path = f"{output_dir}/model/{model_name}/{pipeline_id}/"
    os.makedirs(output_directory_path, exist_ok=True)
    script_path = f"script/run_gpt/run_chatgpt.py"
    cmd = (f"{Conf.PYTHON_INTERPRETER_PATH} {script_path} {data_path} {output_directory_path} {api_key}"
           f" --model_name={model_name}")
    task_logger.info(f">>> {cmd}")
    flag = os.system(cmd)
    return flag


def _run_model(dict_model: dict, version: str, shot_type: str, subject: str, result: list, *args, **kwargs):
    """ run model

    :param dict_model: list of model
    :param shot_type: shot type e.g. zero-shot / five-shot
    :param subject: subject
    :param result: list of result
    """
    dry_run = kwargs.get("dry_run")
    cot = kwargs.get("cot")
    finetune_weights = kwargs.get("finetune_weights")
    need_merge_weights = kwargs.get("need_merge_weights")
    language_type_ = kwargs.get("language_type") or LanguageType.EN.value
    question_type_ = kwargs.get("question_type") or QuestionType.MULTIPLE_CHOICE.value
    metric_name_ = kwargs.get("metric_name")
    rag = kwargs.get("rag")
    pipeline_res_file_path_ = kwargs.get("pipeline_res_file_path")
    breakpoint_file_ = kwargs.get("breakpoint_file") or ""
    breakpoint_pipeline_id_ = kwargs.get("breakpoint_pipeline_id")
    # First generate the explanation and then the reasoning must be a cot case
    pre_gen_explanation_for_inference_ = kwargs.get("pre_gen_explanation_for_inference") if cot else False
    customized_model_package_ = kwargs.get("customized_model_package") or ""
    data_path_ = kwargs.get("data_path") or ""
    api_key_ = kwargs.get("api_key") or ""

    list_pipeline_id = []

    _pre_check_env()
    read_sys_env(Conf.ENV_LIST)

    shot_script = script_factory(shot_type, question_type)

    for model_name, model_type in dict_model.items():
        pipeline_id = breakpoint_pipeline_id_ or CommonHelper.generate_uuid()
        if model_type == ModelType.GPT:
            flag = _run_gpt_script(data_path_, api_key_, pipeline_id, model_name)
        else:
            logger_info = f'[task] `pipeline_id: {pipeline_id}, ' \
                          f'model_name: {model_name}, ' \
                          f'model_type: {model_type}, ' \
                          f'subject: {subject}, ' \
                          f'shot: {shot_type}, ' \
                          f'cot: {cot}, ' \
                          f'rag: {rag}, ' \
                          f'dry_run: {dry_run}, ' \
                          f'language_type: {language_type_}, ' \
                          f'question_type: {question_type_} ' \
                          f'metric_name: {metric_name_} ' \
                          f'{"" if not finetune_weights else f", finetune_weights: {finetune_weights}"} ' \
                          f'need_merge_weights: {need_merge_weights}, '

            task_logger.info(f'{logger_info} start.')
            if pipeline_res_file_path_:
                is_exist, path = CommonHelper.judge_file_or_dir_exist(pipeline_res_file_path_)
                if not is_exist:
                    CommonHelper.create_file(pipeline_res_file_path_)
                with open(pipeline_res_file_path_, 'a') as f:
                    f.write(f'{str(pipeline_id)}, {model_name}, {shot_type}, start\n')
            start_time = time.time()
            bool_flags = ""
            if dry_run:
                bool_flags += " --dry_run "
            if cot:
                bool_flags += " --cot"
            if rag:
                bool_flags += " --rag"
            if need_merge_weights:
                bool_flags += " --need_merge_weights"
            if pre_gen_explanation_for_inference_:
                bool_flags += f" --pre_gen_explanation_for_inference"

            if finetune_weights:
                finetune_weights = f" --finetune_weights {finetune_weights}"
            if language_type_:
                language_type_ = f" --language_type {language_type_}"
            if question_type_:
                question_type_ = f" --question_type {question_type_}"
            if metric_name_:
                metric_name_ = f" --metric_name {metric_name_}"
            if breakpoint_file_:
                breakpoint_file_ = f" --breakpoint_file {breakpoint_file_}"
            if customized_model_package_:
                customized_model_package_ = f" --customized_model_package {customized_model_package_}"

            cmd = f"{Conf.PYTHON_INTERPRETER_PATH} {shot_script} {model_name} {subject} {model_type.name} --version={version} " \
                  f"--pipeline_id={pipeline_id}" \
                  + finetune_weights \
                  + language_type_ \
                  + question_type_ \
                  + metric_name_ \
                  + bool_flags \
                  + breakpoint_file_ \
                  + customized_model_package_
            task_logger.info(f">>> {cmd}")
            flag = os.system(cmd)
        end_time = time.time()
        if model_type != ModelType.GPT:
            list_pipeline_id.append(str(pipeline_id))
        if flag == 0:
            task_logger.info(f"{logger_info} success. time: {round(end_time - start_time, 2)}s")
            result.append(f"{logger_info} success. time: {round(end_time - start_time, 2)}s")
            if pipeline_res_file_path_:
                with open(pipeline_res_file_path_, 'a') as f:
                    f.write(f'{str(pipeline_id)}, {model_name}, {shot_type}, success\n')
        else:
            task_logger.info(f"{logger_info} failed. time': {round(end_time - start_time, 2)}s")
            result.append(f"{logger_info} failed. time: {round(end_time - start_time, 2)}s")
            if pipeline_res_file_path_:
                with open(pipeline_res_file_path_, 'a') as f:
                    f.write(f'{str(pipeline_id)}, {model_name}, {shot_type}, failed\n')
    return list_pipeline_id


def script_factory(shot_type, question_type_: QuestionType):
    if question_type_ == QuestionType.CONFIGURATION_TRANSLATION:
        script = "script/main_configuration_translation.py"
    elif question_type_ == QuestionType.LAB_EXAM:
        script = "script/main_lab_exams.py"
    else:
        if shot_type == 'zero-shot':
            script = 'script/main_zero_shot.py'
        else:
            script = 'script/main_five_shot.py'
    return script


def _get_model_dict(list_model_: list):
    return [{model_: MODEL_DICT_MAPPER.get(model_)} for model_ in list_model_ if model_ in MODEL_DICT_MAPPER]


def _check_input_parameters(**param):
    list_model_ = param.get("list_model", [])
    list_finetune_weights_ = param.get("list_finetune_weights", [])
    if 0 < len(list_finetune_weights_) != len(list_model_):
        raise error_code.ParameterError(
            "Model and number of weights do not match . Please adjust `list_model` and `list_finetune_weights` parameters.")


def _pre_process_input_parameters(**param):
    question_type_ = param.get("question_type", [])
    if question_type_.value == QuestionType.CONFIGURATION_TRANSLATION.value:
        param.update({"list_model": [CONFIGURE_TRANSLATION], "list_subject": [CONFIGURE_TRANSLATION]})
    return param


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--list_model", type=str, nargs='+', default=[], required=True, help='the model list')
    parser.add_argument("--list_subject", type=str, nargs='+', default=[], help='the subject list')
    parser.add_argument("--list_shot_type", type=str, nargs='+', default=['zero-shot'],
                        help='the shot-type list')
    parser.add_argument('--version', default=Conf.DEFAULT_VERSION)
    parser.add_argument('--dry_run', action=argparse.BooleanOptionalAction)
    parser.add_argument('--cot', action=argparse.BooleanOptionalAction)
    parser.add_argument("--list_finetune_weights", type=str, nargs='+', default=[], help='the finetune weights list')
    parser.add_argument("--need_merge_weights", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--language_type', choices=[v.value for v in LanguageType], default=LanguageType.EN.value)
    parser.add_argument("--question_type", choices=[v.value for v in QuestionType],
                        default=QuestionType.MULTIPLE_CHOICE.value)
    parser.add_argument("--metric_name", choices=[v.value for v in MetricName], help='the metric name')
    parser.add_argument('--rag', action=argparse.BooleanOptionalAction)
    parser.add_argument('--breakpoint_file', type=str, help='the breakpoint file path')
    parser.add_argument('--breakpoint_pipeline_id', type=str, help='the breakpoint file path')
    parser.add_argument('--pre_gen_explanation_for_inference', action=argparse.BooleanOptionalAction)
    parser.add_argument('--customized_model_package', type=str, help='the customized')
    parser.add_argument('--data_path', type=str, default='')
    parser.add_argument('--api_key', type=str, default='')

    args = parser.parse_args()
    dry_run_ = args.dry_run or False
    cot_ = args.cot or False
    rag_ = args.rag or False
    list_model = args.list_model
    list_shot_type = args.list_shot_type
    list_finetune_weights = args.list_finetune_weights
    need_merge_weights = args.need_merge_weights
    language_type = get_enum_item_by_value(LanguageType, args.language_type)
    question_type = get_enum_item_by_value(QuestionType, args.question_type)
    list_subject = args.list_subject
    metric_name = get_enum_item_by_value(MetricName, args.metric_name) or get_default_metric(question_type)
    breakpoint_file = args.breakpoint_file
    breakpoint_pipeline_id = args.breakpoint_pipeline_id
    version = args.version
    pre_gen_explanation_for_inference = args.pre_gen_explanation_for_inference
    customized_model_package = args.customized_model_package
    data_path = args.data_path
    api_key = args.api_key

    param = _pre_process_input_parameters(**{
        "list_subject": list_subject,
        "question_type": question_type
    })
    list_subject = param.get("list_subject")

    _check_input_parameters(**{
        "list_model": list_model,
        "list_finetune_weights": list_finetune_weights
    })

    # get dict of model e.g. huggllama/llama-7b ... -> [{huggyllama/llama-7b: ModelType.LLAMA ...}]
    list_dict_model_ = _get_model_dict(list_model)

    result_ = []
    list_pipeline_id = []
    model_index = 0
    pipeline_res_file_path = 'output/run_model/auto_run_model_pipeline_status.txt'
    for model in list_dict_model_:
        for shot_type_ in list_shot_type:
            for subject_ in list_subject:
                pipeline_ids = _run_model(model, version, shot_type_, subject_, result_, **{"dry_run": dry_run_,
                                                                                            "cot": cot_,
                                                                                            "rag": rag_,
                                                                                            "finetune_weights":
                                                                                                list_finetune_weights[
                                                                                                    model_index] if len(
                                                                                                    list_finetune_weights) > model_index else "",
                                                                                            "need_merge_weights": need_merge_weights,
                                                                                            "language_type": language_type.value,
                                                                                            "question_type": question_type.value,
                                                                                            "metric_name": metric_name.value,
                                                                                            "pipeline_res_file_path": pipeline_res_file_path,
                                                                                            "breakpoint_file": breakpoint_file,
                                                                                            "breakpoint_pipeline_id": breakpoint_pipeline_id,
                                                                                            "pre_gen_explanation_for_inference": pre_gen_explanation_for_inference,
                                                                                            "customized_model_package": customized_model_package,
                                                                                            "data_path": data_path,
                                                                                            "api_key": api_key,
                                                                                            },
                                          )
                list_pipeline_id.extend(pipeline_ids)
        model_index += 1

    result_output_path = 'output/run_model/auto_run_model.json'
    is_exist, path = CommonHelper.judge_file_or_dir_exist(result_output_path)

    if question_type.value not in [QuestionType.LAB_EXAM.value, QuestionType.CONFIGURATION_TRANSLATION.value]:
        # get result
        res_file_list = run_get_result(
            list_model, list_subject, list_shot_type,
            list_pipeline_id=list_pipeline_id,
            output_dir='output/model',
            classify_path='',
            cot=cot_,
            result_mark=f'{"_".join(list_subject)}-{"_".join(list_shot_type)}',
            question_type=question_type,
            metric_name=metric_name,
        )
