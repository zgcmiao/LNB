# -*- coding: utf-8 -*-
import argparse
import csv
import json
import os
from collections import defaultdict

import numpy as np
import pandas
import pandas as pd
from matplotlib import pyplot as plt

from conf import Conf, QuestionType, ResultDataFileType, MetricName, get_enum_item_by_value
from data import DataManager
from script import filter_question
from script.helper.answer_helper import check_answer
from script.helper.metric_helper import MetricStrategy
from script.helper.result_helper import ResultStrategy
from script.helper.script_helper import nested_dict, normalize_model_name, read_sys_env

RESULT_FILE_TYPE_MAPPING = {
    'chatgpt3.5': ResultDataFileType.Text,
    'chatgpt4': ResultDataFileType.Text,
    'text-davinci-003': ResultDataFileType.Text,
    'ziya': ResultDataFileType.Text,
    'thudm-glm-130b': ResultDataFileType.GlmJson,
}


def plot_multi_metrics(df, model_names, metrics=None, min_zero_shot_accuracy=None, skip_instruct=False,
                       title=None, output_path=None):
    if metrics is None:
        metrics = ['zero-shot', 'five-shot']
    model_names = list(model_names)
    values = defaultdict(dict)
    for _, row in df.iterrows():
        model_name = row['model']
        if model_name not in model_names:
            continue
        if skip_instruct and (model_name.lower().endswith('-instruct') or model_name.lower().endswith('-chat')):
            model_names.remove(model_name)
            continue
        for metric in metrics:
            value = row[metric]
            values[metric][model_name] = value
        if min_zero_shot_accuracy is not None and values['zero-shot'][model_name] < min_zero_shot_accuracy:
            model_names.remove(model_name)
            continue
    value_lists = [[values[metric][model_name] for model_name in model_names] for metric in metrics]

    fig, ax = plt.subplots(layout='constrained', figsize=(15, 5))
    if title:
        ax.set_title(title)
    ax.set_xlabel('Model')
    ax.set_ylabel('Accuracy')
    ax.set_ylim(0, 1)
    ax.grid(axis='y', alpha=0.5)

    x = np.arange(len(model_names))
    offset = 0
    width = 1 / (len(metrics) + 1)
    for metric, value_list in zip(metrics, value_lists):
        bar = ax.bar(x + offset, value_list, width=width, label=metric)
        ax.bar_label(bar, fmt='%.2f')
        offset += width
    ax.set_xticks(x + (len(metrics) - 1) / 2 * width, labels=model_names,
                  rotation=45, rotation_mode='anchor', ha='right')
    ax.legend(ncols=len(metrics))

    if output_path:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        plt.savefig(output_path)


def _write_to_xlsx(output_dir, collected_with_exam_id, collected_with_target, collected_summary,
                   collected_without_subject, result_mark):
    df = pandas.DataFrame(collected_with_exam_id, columns=['Subject', 'Shot Type', 'Model', 'Pipeline ID', 'Exam ID',
                                                           'Total Questions', 'Correct Questions', 'Accuracy or Score'])
    df_summary = pandas.DataFrame(collected_summary, columns=['Subject', 'Shot Type', 'Model', 'Pipeline ID',
                                                              'Total Questions', 'Correct Questions',
                                                              'Accuracy or Score'])
    df_target = pandas.DataFrame(collected_with_target, columns=['Subject', 'Shot Type', 'Model', 'Pipeline ID',
                                                                 'Label', 'Total Questions', 'Correct Questions',
                                                                 'Accuracy or Score'])
    df_without_subject = pandas.DataFrame(collected_without_subject, columns=['Shot Type', 'Model', 'Total Questions',
                                                                              'Correct Questions', 'Accuracy or Score'])

    # write to excel
    out_file = os.path.join(output_dir, f'{result_mark}_results.xlsx')
    writer = pd.ExcelWriter(out_file)
    df.to_excel(writer, sheet_name='Sheet1', header=['Subject', 'Shot Type', 'Model', 'Pipeline ID', 'Exam ID',
                                                     'Total Questions', 'Correct Questions', 'Accuracy or Score'],
                index=False)
    df_summary.to_excel(writer, sheet_name='Sheet2', header=['Subject', 'Shot Type', 'Model', 'Pipeline ID',
                                                             'Total Questions', 'Correct Questions',
                                                             'Accuracy or Score'],
                        index=False)
    df_target.to_excel(writer, sheet_name='Sheet3', header=['Subject', 'Shot Type', 'Model', 'Pipeline ID', 'Label',
                                                            'Total Questions', 'Correct Questions',
                                                            'Accuracy or Score'],
                       index=False)
    df_without_subject.to_excel(writer, sheet_name='Sheet4', header=['Shot Type', 'Model', 'Total Questions',
                                                                     'Correct Questions', 'Accuracy or Score'],
                                index=False)
    writer.close()
    return out_file


def _save_plt_image_to_pdf(collected_without_subject, output_dir, result_mark):
    df = pd.DataFrame(collected_without_subject, columns=['shot_type', 'model', 'total_questions', 'correct_questions',
                                                          'accuracy_or_score'])
    for i, row in df.iterrows():
        df.at[i, 'model'] = normalize_model_name(row['model'])
    shot_type_list = df['shot_type'].unique()
    df_to_draw = pd.DataFrame()
    df_to_draw['model'] = df.loc[df['shot_type'].isin([shot_type_list[0]])]['model']
    shot_type_list = sorted(shot_type_list, reverse=True)
    for shot_type in shot_type_list:
        df_to_draw[shot_type] = df.loc[df['shot_type'].isin([shot_type])]['accuracy_or_score'].reset_index(drop=True)
    plot_multi_metrics(
        df_to_draw,
        list(df['model']),
        metrics=shot_type_list,
        skip_instruct=False,
        title='Model Accuracy',
        output_path=f'{output_dir}/{result_mark}_result.pdf'
    )


def get_and_save_result(output_paths, answers, subject, shot_type, list_model, list_pipeline_id, labels, category_map,
                        cot, collected_with_exam_id, collected_with_target, collected_summary, question_type,
                        metric_name, total_without_subject, correct_without_subject,
                        default_file_type=ResultDataFileType.Text):
    """
    Statistical result information
    Parameters:
        output_paths: list, List of result files that need to be counted. If `output_paths` exists,
                     `answers` will be ignored.
        answers: dict, List of answers that need to be counted, format: {'key': {'answer': xxx, 'raw_answer': xxx}},
                 `key` is spliced by 'id_title_model', and `answer` is the answer that has been processed.
                 For example, the multiple-choice question is directly 'A', 'B', 'C', 'D' and so on.
                 The fill-in-the-blank question is the answer that the model wants to fill in.
                 `raw_answer` is the original answer answered by the model.
        subject: string
        shot_type: string, zero-shot or five-shot
        list_model: list, If you need to obtain only the statistical results of certain models, you can pass in this
                    parameter. Otherwise, if you pass None, the result information of all models will be counted.
        list_pipeline_id: list, If you need to obtain only the statistical results of certain pipeline_ids, you can pass
                          in this parameter. Otherwise, pass in None, and the result information of all pipeline_ids
                          will be counted.
        labels: dict, correct answer dict. Format: {(id, title): {'answer': xxx, 'answer_content': xxx}}, where answer
                is the correct answer and answer_content is the content corresponding to the correct option in the
                multiple-choice question.
        category_map: dict, Classification information, if none, pass {}
        cot: bool, whether cot
        collected_with_exam_id: list, Statistical result information with exam_id
        collected_with_target: list, Statistical result information with target
        collected_summary: list, Statistical result information summary
        question_type: QuestionType
        metric_name: MetricName
        total_without_subject: dict
        correct_without_subject: dict
        default_file_type: ResultDataFileType

    Returns:
        None
    """
    if not output_paths and not answers:
        raise Exception('Output_paths and answers are all empty! Please set one of them.')
    total_by_model = nested_dict()
    total_by_target = nested_dict()
    total_by_exam_id = nested_dict()
    correct_by_model = nested_dict()
    correct_by_target = nested_dict()
    correct_by_exam_id = nested_dict()

    metric = MetricStrategy(metric_name)

    list_model = [model.replace('/', '-').lower() for model in list_model]
    dict_answer = {}
    for output_path in output_paths:
        model_name = os.path.split(os.path.split(output_path)[-2])[-1].lower()
        if list_model and model_name not in list_model:
            continue

        result_file_type = RESULT_FILE_TYPE_MAPPING.get(model_name, default_file_type)

        if 'auto' in output_path:
            _, full_file_name = os.path.split(output_path)
            pipeline_id = full_file_name.split('auto.')[0]
            pipeline_id = pipeline_id.replace('.', '') if pipeline_id != '' else ''
        else:
            pipeline_id = ''
        if list_pipeline_id and pipeline_id not in list_pipeline_id:
            continue

        result_strategy = ResultStrategy(result_file_type, question_type)
        result_strategy.load_result_data(output_path, cot)
        list_answer = result_strategy.list_answer()
        for key, value in list_answer.items():
            dict_answer[f'{key}_{model_name}'] = value
            dict_answer[f'{key}_{model_name}']['pipeline_id'] = pipeline_id

    if not dict_answer and answers is not None:
        dict_answer.update(answers)
    for key, value in dict_answer.items():
        key = key.split('_')
        id, title, model_name = '_'.join(key[:-2]), key[-2], key[-1]
        pipeline_id = value.get('pipeline_id', '')
        label = labels.get((id, title), {}).get('answer')
        if label is None:
            continue

        # Get the category. If it does not exist in the category_map, the category will be empty
        if (id, title) in category_map:
            t = category_map[(id, title)]
        else:
            t = ''

        # Calculate the total of three dimensions
        if pipeline_id not in total_by_model[subject][shot_type][model_name]:
            total_by_model[subject][shot_type][model_name][pipeline_id] = 0
        total_by_model[subject][shot_type][model_name][pipeline_id] += 1
        if t not in total_by_target[subject][shot_type][model_name][pipeline_id]:
            total_by_target[subject][shot_type][model_name][pipeline_id][t] = 0
        total_by_target[subject][shot_type][model_name][pipeline_id][t] += 1
        if id not in total_by_exam_id[subject][shot_type][model_name][pipeline_id]:
            total_by_exam_id[subject][shot_type][model_name][pipeline_id][id] = 0
        total_by_exam_id[subject][shot_type][model_name][pipeline_id][id] += 1
        if model_name not in total_without_subject[shot_type]:
            total_without_subject[shot_type][model_name] = 0
        total_without_subject[shot_type][model_name] += 1

        # get answer
        metric_result = check_answer(value['answer'], label, metric)

        # If the options do not match, determine whether the content matches.
        if question_type in [QuestionType.MULTIPLE_CHOICE] and metric_result == 0:
            answer_content = labels.get((id, title), {}).get('answer_content')
            if value['raw_answer'].lower().strip().startswith(answer_content.lower()) \
                    or value['raw_answer'].lower().strip().startswith(f'"{answer_content.lower()}"') \
                    or value['raw_answer'].lower().strip().startswith(f"'{answer_content.lower()}'"):
                metric_result = 1
                print(f'id-title: {id}-{title} matches answer content. '
                      f'answer_content: {answer_content}, answer: {value["raw_answer"].strip()}')
        if pipeline_id not in correct_by_model[subject][shot_type][model_name]:
            correct_by_model[subject][shot_type][model_name][pipeline_id] = 0
        correct_by_model[subject][shot_type][model_name][pipeline_id] += metric_result
        if t not in correct_by_target[subject][shot_type][model_name][pipeline_id]:
            correct_by_target[subject][shot_type][model_name][pipeline_id][t] = 0
        correct_by_target[subject][shot_type][model_name][pipeline_id][t] += metric_result
        if id not in correct_by_exam_id[subject][shot_type][model_name][pipeline_id]:
            correct_by_exam_id[subject][shot_type][model_name][pipeline_id][id] = 0
        correct_by_exam_id[subject][shot_type][model_name][pipeline_id][id] += metric_result
        if model_name not in correct_without_subject[shot_type]:
            correct_without_subject[shot_type][model_name] = 0
        correct_without_subject[shot_type][model_name] += metric_result

    for subject, subject_values in total_by_exam_id.items():
        for shot_type, shot_type_values in subject_values.items():
            for model_name, values in shot_type_values.items():
                for pipeline_id, value in values.items():
                    for exam_id, total in value.items():
                        correct = correct_by_exam_id.get(subject, {}).get(shot_type, {}).get(model_name, {}).get(
                            pipeline_id, {}).get(exam_id, 0)
                        accuracy = correct / total if total != 0 else 0
                        collected_with_exam_id.append(
                            [subject, shot_type, model_name, pipeline_id, exam_id, total, correct, accuracy])
    collected_with_exam_id.sort(key=lambda x: x[0])

    for subject, subject_values in total_by_model.items():
        for shot_type, shot_type_values in subject_values.items():
            for model_name, values in shot_type_values.items():
                for pipeline_id, total in values.items():
                    correct_m = correct_by_model.get(subject, {}).get(shot_type, {}).get(model_name, {}).get(
                        pipeline_id)
                    accuracy = correct_m / total if total != 0 else 0
                    collected_summary.append([subject, shot_type, model_name, pipeline_id, total, correct_m, accuracy])
    collected_summary.sort(key=lambda x: x[0])

    for subject, subject_values in total_by_target.items():
        for shot_type, shot_type_values in subject_values.items():
            for model_name, values in shot_type_values.items():
                for pipeline_id, value in values.items():
                    for target, total in value.items():
                        correct_t = correct_by_target.get(subject, {}).get(shot_type, {}).get(model_name, {}).get(
                            pipeline_id, {}).get(target, 0)
                        accuracy = correct_t / total if total != 0 else 0
                        collected_with_target.append(
                            [subject, shot_type, model_name, pipeline_id, target, total, correct_t, accuracy])
    collected_with_target.sort(key=lambda x: x[0])


def run(list_model, list_subject, list_shot_type, list_pipeline_id, output_dir, classify_path, cot,
        result_mark, question_type=QuestionType.MULTIPLE_CHOICE, metric_name=MetricName.Exact,
        default_file_type=ResultDataFileType.Text):
    read_sys_env(Conf.ENV_LIST)

    collected_with_exam_id = []
    collected_with_target = []
    collected_summary = []
    total_without_subject = nested_dict()
    correct_without_subject = nested_dict()
    for subject in list_subject:
        # get all exam questions
        with open(DataManager().get_data_file_path(f"metadata/subjects/{subject}.json"), encoding='utf-8') as f_cfg:
            subject_cfg = json.load(f_cfg)
        exam_files = subject_cfg['exam_files']

        labels = {}
        for exam_path in exam_files:
            with open(DataManager().get_data_file_path(exam_path), encoding='utf-8') as f:
                exam_data = json.load(f)
            exam_id = exam_data['id']
            for q in filter(filter_question, exam_data['questions']):
                if question_type in [QuestionType.MULTIPLE_CHOICE]:
                    choice_contents = {c['name']: c['content'] for c in q['choices']}
                    labels[(exam_id, q['title'])] = {
                        'answer': q['answer']['choice'],
                        'answer_content': choice_contents.get(q['answer']['choice'], '')
                    }
                else:
                    labels[(exam_id, q['title'])] = {
                        'answer': q['answer'],
                        'answer_content': ''
                    }

        # classify
        target_map = {}
        if classify_path and os.path.isfile(classify_path):
            with open(classify_path) as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    id = (line[0], line[1])
                    target_map[id] = line[2]

        # handle all result files
        for shot_type in list_shot_type:
            shot_output_paths = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if (file.endswith(f'{shot_type}.json') or file.endswith(f'{shot_type}.txt')) and subject in file:
                        shot_output_paths.append(os.path.join(root, file))
            if shot_output_paths:
                get_and_save_result(shot_output_paths, None, subject, shot_type, list_model, list_pipeline_id,
                                    labels, target_map, cot, collected_with_exam_id, collected_with_target,
                                    collected_summary, question_type, metric_name, total_without_subject,
                                    correct_without_subject, default_file_type)
    collected_without_subject = []
    for shot_type, shot_type_values in total_without_subject.items():
        for model_name, total in shot_type_values.items():
            correct_t = correct_without_subject.get(shot_type, {}).get(model_name, 0)
            accuracy = correct_t / total if total != 0 else 0
            collected_without_subject.append([shot_type, model_name, total, correct_t, accuracy])
    collected_without_subject.sort(key=lambda x: x[0])
    res_file = _write_to_xlsx(output_dir, collected_with_exam_id, collected_with_target, collected_summary,
                              collected_without_subject, result_mark)

    # _save_plt_image_to_pdf(collected_without_subject, output_dir, result_mark)

    print(f'result file list: {res_file}')
    return res_file


def main():
    """
    Pass in the subject and count the results based on the subject's content. The results are divided into three dimensions:
    1. The accuracy of each model and each set of questions (exam_id)
    2. The accuracy of each model
    3. The accuracy of each model and each label

    The naming rules for the result files are unified as:
        auto.subject-five-shot.json (five-shot)
        auto.subject-zero-shot.json (zero-shot)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', default=Conf.BASE_PATH / 'result/v20230719/auc_result_by_models')
    parser.add_argument('--classify_path', default='')
    parser.add_argument('--cot', action=argparse.BooleanOptionalAction)
    parser.add_argument("--list_model", type=str, nargs='+', default=[], help='the model list')
    parser.add_argument("--list_subject", type=str, nargs='+', default=['security', 'network'],
                        help='the subject list.')
    parser.add_argument("--list_shot_type", type=str, nargs='+', default=['zero-shot', 'five-shot'],
                        help='the shot-type list')
    parser.add_argument("--list_pipeline_id", type=str, nargs='+', default=[],
                        help='the shot-type list')
    parser.add_argument("--question_type", choices=[v.value for v in QuestionType],
                        default=QuestionType.MULTIPLE_CHOICE.value, help='the question type')
    parser.add_argument("--metric_name", choices=[v.value for v in MetricName], default=MetricName.Exact.value,
                        help='the metric name')
    parser.add_argument("--default_file_type", choices=[v.value for v in ResultDataFileType],
                        default=ResultDataFileType.Text.value, help='the metric name')

    args = parser.parse_args()

    output_dir = args.output_dir
    classify_path = args.classify_path
    cot = args.cot or False

    list_model = args.list_model
    list_subject = args.list_subject
    list_shot_type = args.list_shot_type
    list_pipeline_id = args.list_pipeline_id
    question_type = get_enum_item_by_value(QuestionType, args.question_type)
    metric_name = get_enum_item_by_value(MetricName, args.metric_name)
    default_file_type = get_enum_item_by_value(ResultDataFileType, args.default_file_type)

    run(
        list_model=list_model,
        list_subject=list_subject,
        list_shot_type=list_shot_type,
        list_pipeline_id=list_pipeline_id,
        output_dir=output_dir,
        classify_path=classify_path,
        cot=cot,
        result_mark=f'{"_".join(list_subject)}-{"_".join(list_shot_type)}-{metric_name}',
        question_type=question_type,
        metric_name=metric_name,
        default_file_type=default_file_type,
    )


if __name__ == '__main__':
    main()
