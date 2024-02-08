# -*- coding: utf-8 -*-
import enum
import json
import os
import types
from pathlib import Path
from torch import dtype
from utils import CommonHelper


def dict_input_output_file_path_mapper(input_path: str, output_path: str) -> dict:
    """ Get input / output file path mapper

    :param input_path: input path
    :param output_path: output path
    :return: input / output mapper
    """
    dict_mapper = {}

    if not CommonHelper.judge_file_or_dir_exist(output_path):
        CommonHelper.create_file(output_path)

    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            dict_mapper.update(
                {Path(fr'{input_path}/{file}'): Path(fr'{output_path}/{file}') for file in files})
            break
    else:
        input_file_path = Path(input_path)
        dict_mapper.update({Path(fr'{input_file_path}'): Path(
            fr'{output_path}/{input_file_path.name}')})

    return dict_mapper


def yield_questions_from_input_files(input_output_mapper):
    for input_path, output_path in input_output_mapper.items():
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            id = data['id']
            title = data['title']
            questions = data['questions']
            yield id, title, questions, output_path, len(questions)


class ParametersEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, types.FunctionType):
            return obj.__name__
        elif isinstance(obj, enum.Enum):
            return obj.name
        elif isinstance(obj, dtype):
            return obj.__str__()

        return json.JSONEncoder.default(self, obj)
