# -*- coding: utf-8 -*-
import json

from tqdm import tqdm

from model import ModelType, QuestionType
from utils.decorator import pipeline_logger_wrapper
from .pipeline_base import BaseEvaluationPipeline
from .pipeline_helper import yield_questions_from_input_files
from pathlib import Path
from utils import pipeline_logger, CommonHelper
from conf import Conf

LOGGER_PREFIX = "LabPipeline"


class LabEvaluationPipeline(BaseEvaluationPipeline):
    """ Lab evaluation pipeline

    """

    def __init__(self,
                 model_type: ModelType,
                 model_name: str,
                 *args,
                 **kwargs):
        """Init GlmEvaluationPipeline class

                :param model_type: model type, e.g. LLAMA
                :param model_name: model name, e.g. llama-7b
                """
        super().__init__(model_type, model_name, *args, **kwargs)

    key_expression = QuestionType.LAB_EXAM.name

    def _pre_process_init_model_process(self, *args, **kwargs):
        """ Process: Pre init evaluation model process

        Pre-process init evaluation model
        :param args: args
        :param kwargs: kwargs
        """
        pass

    def _init_model_process(self, *args, **kwargs):
        """ Process: Init evaluation model process

        Init evaluation model
        :param args: args
        :param kwargs: kwargs
        """
        super()._init_model_process(*args, **kwargs)

    def _pre_process_session_generation_process(self, *args, **kwargs):
        """ Process: Pre process session generation process

        Pre-process generate model session
        :param args: args
        :param kwargs: kwargs
        """
        super()._pre_process_session_generation_process(*args, **kwargs)

    def _session_generation_process(self, *args, **kwargs):
        """ Process: Session generation process

        Generate model session
        :param args: args
        :param kwargs: kwargs
        :return: session
        """
        super()._session_generation_process(*args, **kwargs)

    def _pre_process_result_generation_process(self, *args, **kwargs):
        """ Process: Pre process result generation process

        Pre-process generate model result
        :param args: args
        :param kwargs: kwargs
        """
        super()._pre_process_result_generation_process(*args, **kwargs)

    @pipeline_logger_wrapper("result_generation_process")
    def _result_generation_process(self, *args, **kwargs):
        """ Process: Result generation process

        Generate model result
        :param args: args
        :param kwargs: kwargs
        """

        self.__prompt_generator_func = self._pipeline_param.get("prompt_generator_func")
        # print(self.__prompt_generator_func)
        #
        self._overview_result_path = Path(self._output_path).parent
        name = Path(Conf.BASE_PATH / self._output_path).name
        question_type = self._pipeline_param.get('question_type')
        subject = self._pipeline_param.get('subject')

        if subject == 'intent_completion_command_execution':
            for id, exam_title, exam_questions, output_path, total_num in yield_questions_from_input_files(self._dict_mapper):
                print(output_path)
                is_exist, path = CommonHelper.judge_file_or_dir_exist(Conf.BASE_PATH / output_path)
                if not is_exist:
                    CommonHelper.create_file(path)
                self.save_to_overview_result(exam_title, name, total_num)
                for question in tqdm(exam_questions):
                    if question['with_level']:
                        title = '&'.join([question['protocol'], question['lab'], question['level']])
                    else:
                        title = '&'.join([question['protocol'], question['lab']])
                    # item_title = question['title']
                    # item_id = question['exam_id']
                    item_prompt_text = self._model_instance.request_prompt_generator(item_content=question,
                                                                                    prompt_generator_func=self.__prompt_generator_func)
                    self.__prompt_text = item_prompt_text
                    result = self._model_instance.result_generator(prompt_text=self.__prompt_text)
                    print("\n--------PROMPT--------\n" + self.__prompt_text)
                    print("\n--------ANSWER--------\n" + result)
                    with open(path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({'title': title, 'question': question, 'answer': result}, #question['exam_type']
                                        ensure_ascii=False) + '\n')

                pipeline_logger.info(f"pipeline id: `{self.pipeline_id}`, output path: {path}")

        elif subject == 'intent_completion_topo_comprehension':
            for id, exam_title, exam_questions, output_path, total_num in yield_questions_from_input_files(self._dict_mapper):
                print(id, exam_title, exam_questions, output_path, total_num)
                is_exist, path = CommonHelper.judge_file_or_dir_exist(Conf.BASE_PATH / output_path)
                if not is_exist:
                    CommonHelper.create_file(path)
                self.save_to_overview_result(exam_title, name, total_num)
                print(exam_questions)
                for question in tqdm(exam_questions):
                    id = question['id']
                    question_type = question['question_type']
                    prompt = question['content']
                    item_prompt_text = self._model_instance.request_prompt_generator(item_content=prompt,
                                                                                     prompt_generator_func=self.__prompt_generator_func) #item_prompt_text=prompt=question['content']
                    self.__prompt_text = item_prompt_text
                    result = self._model_instance.result_generator(prompt_text=self.__prompt_text)
                    print("\n--------PROMPT--------\n" + self.__prompt_text)
                    print("\n--------ANSWER--------\n" + result)
                    with open(path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({'question_type': question_type, 'prompt':prompt, 'answer': result}, #question['exam_type']
                                        ensure_ascii=False) + '\n')


        elif subject == 'operational_safety':
            for id, exam_title, exam_questions, output_path, total_num in yield_questions_from_input_files(self._dict_mapper):
                print(output_path)
                is_exist, path = CommonHelper.judge_file_or_dir_exist(Conf.BASE_PATH / output_path)
                if not is_exist:
                    CommonHelper.create_file(path)
                self.save_to_overview_result(exam_title, name, total_num)
                for question in tqdm(exam_questions):
                    id = question['id']
                    property = question['property']
                    prompt = question['question']
                    item_prompt_text = self._model_instance.request_prompt_generator(item_content=prompt,
                                                                                     prompt_generator_func=self.__prompt_generator_func) #item_prompt_text=prompt=question['content']
                    self.__prompt_text = item_prompt_text
                    result = self._model_instance.result_generator(prompt_text=self.__prompt_text)
                    print("\n--------PROMPT--------\n" + self.__prompt_text)
                    print("\n--------ANSWER--------\n" + result)
                    with open(path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({'question_type': id, 'prompt': prompt, 'answer': result},
                                          ensure_ascii=False) + '\n')


    def _post_process_result_generation_process(self, *args, **kwargs):
        """ Process: Post process result generation process

        Pre-post generate model result
        :param args: args
        :param kwargs: kwargs
        """
        pass