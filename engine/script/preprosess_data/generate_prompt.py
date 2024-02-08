# -*- coding: utf-8 -*-
import json

import argparse
from pathlib import Path

from data import DataManager
from conf import Conf, LanguageType, QuestionType, get_enum_item_by_value
from script import format_question, filter_question
from script.helper.prompt_helper import question_format_convert_handler, QuestionPromptStrategy


def generate_prompt_text(subject_: str, shot_type_: str, language_type_: LanguageType,
                         question_type_: QuestionType = QuestionType.MULTIPLE_CHOICE,
                         **kwargs):

    with open(DataManager().get_data_file_path(f"metadata/subjects/{subject_}.json"), encoding="utf-8") as f_cfg:
        subject_cfg = json.load(f_cfg)
    subject_example_keys = set((e['exam_id'], e['question_id']) for e in subject_cfg['examples'])
    subject_example_questions = []
    subject_test_questions = []
    for example_path in subject_cfg['example_files']:
        with open(DataManager().get_data_file_path(example_path)) as f_in:
            exam_data = json.load(f_in)
            exam_id = exam_data['id']
            questions = exam_data['questions']
            for q in filter(filter_question, questions):
                q['exam_id'] = exam_id
                q_key = (exam_id, q['title'])
                if q_key in subject_example_keys:
                    subject_example_questions.append(q)

    for exam_path in subject_cfg['exam_files']:
        with open(DataManager().get_data_file_path(exam_path), encoding="utf-8") as f_in:
            exam_data = json.load(f_in)
            exam_id = exam_data['id']
            questions = exam_data['questions']
            for q in filter(filter_question, questions):
                q['exam_id'] = exam_id
                q_key = (exam_id, q['title'])
                if q_key not in subject_example_keys:
                    subject_test_questions.append(q)

    print(f'exam_files: {subject_cfg["exam_files"]}')

    strategy = QuestionPromptStrategy(question_type_)
    prompt_header_parts = [strategy.generate_prompt_header(
        **{"subject_name": subject_cfg["name"],
           "subject_zh_name": subject_cfg.get("zh_name", subject_cfg["name"]),
           "target_language": language_type_})]

    if shot_type_ == 'five-shot':
        for q in subject_example_questions:
            dict_inputs = question_format_convert_handler(raw_question_type=QuestionType.MULTIPLE_CHOICE,
                                                          target_question_type=question_type,
                                                          raw_question=q, **{"cot": None,
                                                                             "with_answer": True,
                                                                             "target_language": language_type_})
            prompt_header_parts.append(format_question(q, question_type_, dict_inputs=dict_inputs))
    prompt_header = '\n\n'.join(prompt_header_parts)
    list_prompt_content_ = []
    n = 0
    for question in subject_test_questions:
        prompt_content = prompt_header + '\n\n' + format_question(question, question_type_, **{"cot": None,
                                                                                               "with_answer": False,
                                                                                               "target_language": language_type_})

        list_prompt_content_.append({'id': question['exam_id'], 'title': question['title'], 'prompt': prompt_content,
                                     'choice': strategy.get_question_correct_answer(question)})
        n += 1
    print(f'result: {n}')
    prompt_text_name_ = f'list_{subject_}_prompt_{shot_type_}_{language_type_.name}.json'
    return prompt_text_name_, list_prompt_content_


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subject')
    parser.add_argument('shot_type')
    parser.add_argument('--language_type', choices=[v.value for v in LanguageType], default=LanguageType.EN.value)
    parser.add_argument("--question_type", choices=[v.value for v in QuestionType],
                        default=QuestionType.MULTIPLE_CHOICE.value)
    args = parser.parse_args()

    subject = args.subject
    shot_type = args.shot_type
    language_type = get_enum_item_by_value(LanguageType, args.language_type)
    question_type = get_enum_item_by_value(QuestionType, args.question_type)

    output_path = Conf.BASE_PATH / 'output/prompt/'
    Path(output_path).mkdir(parents=True, exist_ok=True)

    prompt_text_name, list_prompt_content = generate_prompt_text(subject, shot_type, language_type, question_type)
    with open(output_path / prompt_text_name, 'w', encoding="utf-8") as w_out:
        w_out.write(json.dumps(list_prompt_content, ensure_ascii=False))
    print(f'generate prompt success. output path: {output_path / prompt_text_name}')
