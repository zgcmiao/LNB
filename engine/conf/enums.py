# -*- coding: utf-8 -*-
from enum import Enum

class ModelType(Enum):
    LLAMA = 1
    GPT = 2
    CHATGLM = 3
    FALCON = 4
    MOSS = 5
    BAICHUAN = 6
    GLM = 7
    LLAMA_LOAD_MODEL = 8
    LLAMA2 = 9
    MIXTRAL = 10
    CHATGLM2 = 11
    CUSTOMIZED = 12


class TransformersLocalRemoteType(Enum):
    LOCAL = 0
    REMOTE = 1


class LanguageType(Enum):
    EN = "en"
    ZH = "zh"


class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    CLOZE = "cloze"
    QUESTION_AND_ANSWER = "qa"
    LAB_EXAM = "lab_exam"
    CONFIGURATION_TRANSLATION = "configuration_translation"


class ResultDataFileType(Enum):
    NormalJson = 'normal_json'
    Text = 'text'
    GlmJson = 'glm_json'


class StatisticsType(Enum):
    """
    statistics type
    """
    Summary = 'summary'
    ExamID = 'exam_id'
    CategoryType = 'category_type'


class IsRepeatQuestionContent(Enum):
    RepeatQuestionContent = 'repeat'
    NoRepeatQuestionContent = 'no_repeat'


class MetricName(Enum):
    Exact = 'exact'
    Bleu = 'bleu'
    Rouge = 'rouge'


def get_enum_item_by_value(enum_class, value):
    for enum_constant in enum_class:
        if enum_constant.value == value:
            return enum_constant
