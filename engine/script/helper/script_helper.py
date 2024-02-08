# -*- coding: utf-8 -*-
import os
import re
import uuid
from collections import defaultdict
from model import ModelType
from conf import QuestionType, error_code, MetricName
from script.helper.prompt_helper import QuestionPromptStrategy

MODEL_DICT_MAPPER = {
    "huggyllama/llama-7b": ModelType.LLAMA,
    "huggyllama/llama-13b": ModelType.LLAMA,
    "huggyllama/llama-30b": ModelType.LLAMA,
    "huggyllama/llama-65b": ModelType.LLAMA,
    "meta-llama/Llama-2-7b-hf": ModelType.LLAMA2,
    "meta-llama/Llama-2-7b-chat-hf": ModelType.LLAMA2,
    "meta-llama/Llama-2-13b-hf": ModelType.LLAMA2,
    "meta-llama/Llama-2-13b-chat-hf": ModelType.LLAMA2,
    "meta-llama/Llama-2-70b-hf": ModelType.LLAMA2,
    "meta-llama/Llama-2-70b-chat-hf": ModelType.LLAMA2,
    "tiiuae/falcon-7b": ModelType.FALCON,
    "tiiuae/falcon-7b-instruct": ModelType.FALCON,
    "tiiuae/falcon-40b": ModelType.FALCON,
    "tiiuae/falcon-40b-instruct": ModelType.FALCON,
    "THUDM/glm-10b": ModelType.GLM,
    "THUDM/chatglm-6b": ModelType.CHATGLM,
    "THUDM/chatglm2-6b": ModelType.CHATGLM,
    "baichuan-inc/baichuan-7B": ModelType.BAICHUAN,
    "baichuan-inc/Baichuan-13B-Base": ModelType.BAICHUAN,
    "baichuan-inc/Baichuan-13B-Chat": ModelType.BAICHUAN,
    "fnlp/moss-moon-003-base": ModelType.MOSS,
    "fnlp/moss-moon-003-sft": ModelType.MOSS,
    "text-davinci-003": ModelType.GPT,
    "gpt-3.5-turbo": ModelType.GPT,
    "gpt-4": ModelType.GPT,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": ModelType.MIXTRAL,
    "mistralai/Mixtral-8x7B-v0.1": ModelType.MIXTRAL,
    "customized-model": ModelType.CUSTOMIZED,
}


def detect_model_type(model_name_or_path: str):
    for enum_type in ModelType:
        if model_name_or_path.lower() == enum_type.name.lower():
            return enum_type
    raise error_code.ParameterError(f'Unable to detect model type `{model_name_or_path}`.')


def filter_question(question):
    if question.get('with_images', False):
        return False
    if isinstance(question.get("answer", {}), dict) and not isinstance(question.get("answer", {}).get("choice", ""), str):
        return False
    if isinstance(question.get("answer", {}), dict) and len(question.get("answer", {}).get("choice", "")) > 1:
        return False
    return True


def format_question(question: dict, question_type: QuestionType = QuestionType.MULTIPLE_CHOICE, dict_inputs: dict = None,
                    *args, **kwargs):
    strategy = QuestionPromptStrategy(question_type)
    if not dict_inputs:
        dict_inputs = strategy.normalize_generating_prompts_inputs_func(question, *args, **kwargs)
    return strategy.generate_prompt(*args, **dict_inputs)


re_used_map = {}


def get_answer(answer, cot):
    r1 = r'(.)*Answer( )?: (([A-I](,)? )*(and )?([A-I])?)'
    r2 = r'(.)*Answer:The correct ((option)|(answers)) for this question would be ([A-I](,)? )*(and )?([A-I])?'
    r3 = r'(.)*The correct option here would be (([A-I])+)'
    r4 = r'(.)*答案：(([A-I])+)'
    r5 = r'(.)*The correct answers are (([A-I](,)? )*(and )?([A-I])?)'
    r6 = r'(\d)\.( |\n)*Answer( )*:(([A-I](,)? )*(and )?([A-I])+)'
    r7 = r'(\d)\.( |\n)*(([A-I](,)? )*(and )?([A-I])+)'
    r8 = r'\(([A-I])\)'
    r9 = r'\"([A-I])'
    r10 = r'(.)*The correct answer is( |: \n)([A-I])'
    r11 = r'(.)*The answer is( |: \n)([A-I])'
    r12 = r'(\n)*( )*([A-I])\.'
    r13 = r'The answer to the question is ([A-I])'
    r14 = r'([A-I])  '
    r15 = r'([A-I]) ---(-)*'
    r16 = r"answer is ([a-dA-D]+)"
    r17 = r'(.)*答案(是|为)?(选项)?(:| |：)?([A-I])'
    r18 = r'(.)*正确的选项是([A-I])'
    r19 = r'(.)*(选项)?([A-I])是(本题的)?正确答案'
    r20 = r'([A-I]):'
    r21 = r'\'([A-I])'
    r22 = r'([A-I]),'
    r23 = r'([A-I])</s>'
    r24 = r"answer to the question is ([a-dA-D]+)"
    r25 = r"answer is( |: \n)([a-dA-D]+)"
    r26 = r'(.)*Answer:The correct ((option)|(answers)) for this question would have been ([A-I](,)? )*(and )?([A-I])?'
    r27 = r'(.)*The correct option here would hive been (([A-I])+)'
    r28 = r'(.)*正确(答案|选项)?(是|为)?(:|：)?(\s)?(([A-I])+)'
    r29 = r'(.)*答(:|：)?(\s)?(选)?(\s)?(正确答案|【正确答案】)?(:|：)?(\s)?(([A-I])+)'

    re_list = [
        {'pattern': r1, 'group_num': 3},
        {'pattern': r2, 'group_num': 5},
        {'pattern': r3, 'group_num': 2},
        {'pattern': r4, 'group_num': 2},
        {'pattern': r5, 'group_num': 2},
        {'pattern': r6, 'group_num': 4},
        {'pattern': r7, 'group_num': 3},
        {'pattern': r8, 'group_num': 1},
        {'pattern': r9, 'group_num': 1},
        {'pattern': r10, 'group_num': 3},
        {'pattern': r11, 'group_num': 3},
        {'pattern': r12, 'group_num': 3},
        {'pattern': r13, 'group_num': 1},
        {'pattern': r14, 'group_num': 1},
        {'pattern': r15, 'group_num': 1},
        {'pattern': r17, 'group_num': 5},
        {'pattern': r18, 'group_num': 2},
        {'pattern': r19, 'group_num': 3},
        {'pattern': r20, 'group_num': 1},
        {'pattern': r21, 'group_num': 1},
        {'pattern': r22, 'group_num': 1},
        {'pattern': r23, 'group_num': 1},
        {'pattern': r28, 'group_num': 6},
        {'pattern': r29, 'group_num': 9},
    ]

    cot_re_list = [
        {'pattern': r16, 'group_num': 1},
        {'pattern': r24, 'group_num': 1},
        {'pattern': r25, 'group_num': 1},
        {'pattern': r10, 'group_num': 3},
        {'pattern': r11, 'group_num': 3},
        {'pattern': r12, 'group_num': 3},
        {'pattern': r13, 'group_num': 1},
        {'pattern': r1, 'group_num': 3},
        {'pattern': r2, 'group_num': 5},
        {'pattern': r3, 'group_num': 2},
        {'pattern': r26, 'group_num': 5},
        {'pattern': r27, 'group_num': 2},
        {'pattern': r4, 'group_num': 2},
        {'pattern': r5, 'group_num': 2},
        {'pattern': r6, 'group_num': 4},
        {'pattern': r7, 'group_num': 3},
        {'pattern': r8, 'group_num': 1},
        {'pattern': r9, 'group_num': 1},
        {'pattern': r14, 'group_num': 1},
        {'pattern': r15, 'group_num': 1},
        {'pattern': r17, 'group_num': 5},
        {'pattern': r18, 'group_num': 2},
        {'pattern': r19, 'group_num': 3},
    ]

    # print("------------RAW------------")
    if cot:
        answer = re.sub('Question:(.*)', '',
                        answer, flags=re.IGNORECASE | re.DOTALL)
    # print(answer)

    group_num = 0
    match = None
    rl = cot_re_list if cot else re_list
    for r in rl:
        matching = re.search if cot else re.match
        match = matching(r['pattern'], answer, re.S)
        if match:
            group_num = r['group_num']
            if r['pattern'] not in re_used_map:
                re_used_map[r['pattern']] = 0
            re_used_map[r['pattern']] += 1
            break
    if not match:
        return []

    ans_str = match.group(group_num)
    # print("------------ANSWER------------")
    # print(ans_str)
    ans_str = ans_str.replace(', ', '')
    ans_str = ans_str.replace(' and ', '')
    ans_str = ans_str.replace(' & ', '')
    ans_str = ans_str.replace(' ', '')

    # print("------------CLEANED ANSWER------------")
    # print(ans_str)

    if len(ans_str) == 1:
        return [ans_str]
    else:
        return [k for k in ans_str]


def is_uuid(string):
    try:
        uuid.UUID(string)
        return True
    except ValueError:
        return False


def nested_dict():
    """
    Nested dict
    """
    return defaultdict(nested_dict)


def is_contain_chinese(s):
    for ch in s:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def get_default_metric(question_type):
    if question_type == QuestionType.MULTIPLE_CHOICE:
        return MetricName.Exact
    elif question_type == QuestionType.CLOZE:
        return MetricName.Bleu
    elif question_type == QuestionType.QUESTION_AND_ANSWER:
        return MetricName.Bleu
    elif question_type == QuestionType.LAB_EXAM:
        return MetricName.Bleu
    elif question_type == QuestionType.CONFIGURATION_TRANSLATION:
        return MetricName.Bleu


def read_sys_env(list_env):
    """ read env setting from conf

    """

    for key, val in list_env.items():
        os.environ[f"{key}"] = val


def normalize_model_name(name):
    prefixes = [
        'huggyllama-',
        'meta-llama-',
        'tiiuae-',
        'thudm-'
    ]
    suffixes = [
        '-hf'
    ]
    for p in prefixes:
        if name.startswith(p):
            name = name[len(p):]
            break
    for s in suffixes:
        if name.endswith(s):
            name = name[:-len(s)]
            break
    return name
