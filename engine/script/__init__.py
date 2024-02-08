# -*- coding: utf-8 -*-
from script.helper.prompt_helper import QuestionPromptStrategy
from script.helper.script_helper import detect_model_type, filter_question, format_question, get_answer, MODEL_DICT_MAPPER, is_uuid, \
    read_sys_env, get_default_metric
from .main_zero_shot import run as run_zero_shot
from .main_five_shot import run as run_five_shot
from script.postprosess_result.get_result import run as run_get_result
from script.preprosess_data.generate_prompt import generate_prompt_text
# from script.run_gpt.openai_proxy import openai
import openai
from .postprosess_result.analyze_configure_translation_result import compute_score_line_level, \
    compute_score_block_level, cal_trans_precision_recall
