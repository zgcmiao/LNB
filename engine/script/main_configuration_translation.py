# -*- coding: utf-8 -*-
import argparse
import os
from pathlib import Path
from conf import QuestionType, LanguageType, Conf, ModelType, MetricName, get_enum_item_by_value
from data import DataManager
from evaluation_pipeline import PipelineManager
from script import detect_model_type, get_default_metric
from utils import CommonHelper

CONFIGURE_TRANSLATION = "network_configure_translation"
CONFIGURE_TRANSLATION_FILE_FORMAT = '%s.auto.%s-zero-shot.json'
DEFAULT_SHOT_TYPE = "zero-shot"


def _get_output_name(model_name, finetune_weights):
    if finetune_weights:
        if Path(finetune_weights).is_dir():
            output_model_name = Path(finetune_weights).name.replace('/', '-')
        else:
            output_model_name = finetune_weights.replace('/', '-')
    else:
        output_model_name = model_name.replace('/', '-')
    return output_model_name


def run(model_name: str, version: str, model_type: ModelType, subject, data=None, data_dir=None, output_dir='output',
        *args, **kwargs):
    """ run configuration translation

    :param model_name: model name
    :param model_type: model type
    :param data: data
    :param data_dir: data directory
    :param max_new_token: max new token
    :param output_dir: output dir
    :param args: args dir
    :param kwargs: kwargs
    """
    cot = kwargs.get('cot')
    dry_run = kwargs.get("dry_run")
    pipeline_id = kwargs.get("pipeline_id")
    finetune_weights = kwargs.get("finetune_weights")
    need_merge_weights = kwargs.get("need_merge_weights")
    question_type = kwargs.get("question_type") or QuestionType.MULTIPLE_CHOICE
    metric_name = kwargs.get("metric_name") or get_default_metric(question_type)
    pre_gen_explanation_for_inference = kwargs.get("pre_gen_explanation_for_inference") if cot else False

    def _prompt_func(**kwargs):
        question_item_content = kwargs["item_content"]["prompt"]
        return question_item_content

    input_file_or_directory_path = data
    output_directory_path = f"{output_dir}/model/{_get_output_name(model_name, finetune_weights)}/"
    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path)

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
                                                                           "cot_no_explanation_prompt_generator_func": None,
                                                                       },
                                                                       model_params={
                                                                           "finetune_weights": finetune_weights,
                                                                           "need_merge_weights": need_merge_weights
                                                                       },
                                                                       )
    pipeline_instance.run_step_by_processes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name_or_path')
    parser.add_argument('subject', default=("%s" % CONFIGURE_TRANSLATION))
    parser.add_argument('model_type')
    parser.add_argument('--data', default=DataManager().get_data_file_path(
        "question_bank/written_exam/network_configure_translation.json"))
    parser.add_argument('--output_dir', default='output')
    parser.add_argument('--version', default=Conf.DEFAULT_VERSION)
    parser.add_argument('--data_dir', default=None)
    parser.add_argument('--cot', action=argparse.BooleanOptionalAction)
    parser.add_argument('--rag', action=argparse.BooleanOptionalAction)
    parser.add_argument('--dry_run', action=argparse.BooleanOptionalAction)
    parser.add_argument('--pipeline_id', default=None)
    parser.add_argument("--finetune_weights", default=None)
    parser.add_argument("--need_merge_weights", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--language_type', choices=[v.value for v in LanguageType], default=LanguageType.EN.value)
    parser.add_argument("--question_type", choices=[v.value for v in QuestionType],
                        default=QuestionType.MULTIPLE_CHOICE.value)
    parser.add_argument("--metric_name", choices=[v.value for v in MetricName], help='the metric name')
    parser.add_argument("--breakpoint_file", default=None, help='the breakpoint file path')
    parser.add_argument("--json_dynamic_params", default=None, help='pass the params by json str')
    parser.add_argument('--pre_gen_explanation_for_inference', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    model_name_or_path = args.model_name_or_path
    subject = args.subject
    model_type = detect_model_type(args.model_type)
    data = args.data
    data_dir = args.data_dir
    output_dir = args.output_dir
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

    run(model_name_or_path, version, model_type, subject, data, data_dir, output_dir,
        **{"dry_run": dry_run, "pipeline_id": pipeline_id,
           "cot": cot,
           "rag": rag,
           "finetune_weights": finetune_weights,
           "need_merge_weights": need_merge_weights,
           "language_type": language_type,
           "question_type": question_type,
           "metric_name": metric_name,
           "breakpoint_file": breakpoint_file,
           "json_dynamic_params": json_dynamic_params,
           "pre_gen_explanation_for_inference": pre_gen_explanation_for_inference})


if __name__ == '__main__':
    import time

    begin_time = time.time()
    main()
    end_time = time.time()
    time_cost = int(end_time - begin_time)
