# -*- coding: utf-8 -*-
import json
from pathlib import Path

import yaml
from tqdm import tqdm
from script import run_get_result
from conf import Conf, error_code, ModelType
from model import ModelManager
from utils import pipeline_logger, CommonHelper
from utils.decorator import pipeline_logger_wrapper
from .pipeline_base_abstract import BaseEvaluationPipelineAbstract
from .pipeline_helper import dict_input_output_file_path_mapper, yield_questions_from_input_files, \
    ParametersEncoder

OVERVIEW_RESULT_JSON_FILE = "overview_result.json"


class BaseEvaluationPipeline(BaseEvaluationPipelineAbstract):
    """ Evaluation pipeline base

    """

    def __init__(self,
                 model_type: ModelType,
                 model_name: str,
                 *args,
                 **kwargs):
        """Init EvaluationPiplineBase class

                :param model_type: model type, e.g. LLAMA
                :param model_name: model name, e.g. llama-7b
                """
        self.__dry_run = False
        super().__init__(model_type, model_name, *args, **kwargs)

    @pipeline_logger_wrapper("pre_process_init_model_process")
    def _pre_process_init_model_process(self, *args, **kwargs):
        """ Process: Pre init evaluation model process

        Pre-process init evaluation model
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @pipeline_logger_wrapper("init_model_process")
    def _init_model_process(self, *args, **kwargs):
        """ Process: Init evaluation model process

        Init evaluation model
        :param args: args
        :param kwargs: kwargs
        """
        if self.model_param.get("model_pipeline_params", {}).get("model", ''):
            self.pipeline_param.update({"model": self.model_param.get("model_pipeline_params", {}).get("model")})
        self._model_instance = ModelManager(Conf.DEFAULT_VERSION).get_model_instance(self.model_type,
                                                                                     self.model_name,
                                                                                     *args,
                                                                                     **self._model_param)

    @pipeline_logger_wrapper("pre_process_session_generation_process")
    def _pre_process_session_generation_process(self, *args, **kwargs):
        """ Process: Pre process session generation process

        Pre-process generate model session
        :param args: args
        :param kwargs: kwargs
        """
        self.__prompt_generator_func = self._pipeline_param.get("prompt_generator_func")
        kwargs.update({"prompt_generator_func": self.__prompt_generator_func})
        self._model_instance.pre_process_session_generator(*args, **kwargs)

    @pipeline_logger_wrapper("session_generation_process")
    def _session_generation_process(self, *args, **kwargs):
        """ Process: Session generation process

        Generate model session
        :param args: args
        :param kwargs: kwargs
        :return: session
        """
        self._model_instance.session_generator()

    @pipeline_logger_wrapper("pre_process_result_generation_process")
    def _pre_process_result_generation_process(self, *args, **kwargs):
        """ Process: Pre process result generation process

        Pre-process generate model result
        :param args: args
        :param kwargs: kwargs
        """
        input_file_or_directory_path_ = self._pipeline_param.get("input_file_or_directory_path")
        output_directory_path_ = self._pipeline_param.get("output_directory_path")
        if not input_file_or_directory_path_ or not output_directory_path_:
            raise error_code.ParameterError(
                f"`input_file_or_directory_path` or `output_directory_path` need to specify.")

        # handle input and output mapper
        self._dict_mapper = dict_input_output_file_path_mapper(input_file_or_directory_path_,
                                                               output_directory_path_)
        self._output_path = output_directory_path_

    @pipeline_logger_wrapper("result_generation_process")
    def _result_generation_process(self, *args, **kwargs):
        """ Process: Result generation process

        Generate model result
        :param args: args
        :param kwargs: kwargs
        """
        self.__prompt_generator_func = self._pipeline_param.get("prompt_generator_func")
        # Overview of results for all models
        self._overview_result_path = Path(self._output_path).parent
        name = Path(Conf.BASE_PATH / self._output_path).name
        for id, exam_title, exam_questions, output_path, total_num in yield_questions_from_input_files(self._dict_mapper):
            is_exist, path = CommonHelper.judge_file_or_dir_exist(Conf.BASE_PATH / output_path)
            if not is_exist:
                CommonHelper.create_file(path)
            self.save_to_overview_result(exam_title, name, total_num)
            for question in tqdm(exam_questions):
                item_title = question['title']
                item_id = question['exam_id']
                item_prompt_text = self._model_instance.request_prompt_generator(item_content=question,
                                                                                 prompt_generator_func=self.__prompt_generator_func)
                self.__prompt_text = item_prompt_text
                item_result = self._model_instance.result_generator(prompt_text=self.__prompt_text)
                print("\n--------PROMPT--------\n" + self.__prompt_text)
                print("\n--------ANSWER--------\n" + item_result)
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'id': item_id, 'title': item_title, 'answer': item_result},
                                       ensure_ascii=False) + '\n')

            pipeline_logger.info(f"pipeline id: `{self.pipeline_id}`, output path: {path}")

    def save_to_overview_result(self, exam_title, name, total_num):
        """ save to overview result file

        """
        overview_path = Path(Conf.BASE_PATH / self._overview_result_path / OVERVIEW_RESULT_JSON_FILE)
        if Path.exists(overview_path):
            with open(overview_path, 'r', encoding='utf-8') as overview_read:
                lines = overview_read.readlines()
                existed = False
                for line in lines:
                    if self.pipeline_id in line:
                        existed = True
                        break
                if not existed:
                    with open(overview_path, 'a', encoding='utf-8') as overview_write:
                        overview_write.write(json.dumps({"model_name": name,
                                                         "pipeline_id": self.pipeline_id,
                                                         "exam_info": {"subject": exam_title, "total_num": total_num}},
                                                        ensure_ascii=False) + '\n')


        else:
            with open(overview_path, 'w', encoding='utf-8') as overview_write:
                overview_write.write(json.dumps({"model_name": name,
                                                 "pipeline_id": self.pipeline_id,
                                                 "exam_info": {"subject": exam_title, "total_num": total_num}},
                                                ensure_ascii=False) + '\n')

    @pipeline_logger_wrapper("post_process_result_generation_process")
    def _post_process_result_generation_process(self, *args, **kwargs):
        """ Process: Post process result generation process

        Pre-post generate model result
        :param args: args
        :param kwargs: kwargs
        """
        if not hasattr(self, "_output_path") or self._output_path is None:
            return

        param_dict = {}
        param_dict.update({"pipeline_param": self.pipeline_param})
        param_dict.update({"model_param": self.model_param})
        param_dict_json_str = json.dumps(param_dict, cls=ParametersEncoder)
        param_dict_yaml = yaml.load(param_dict_json_str, Loader=yaml.FullLoader)

        BaseEvaluationPipeline.__write_pipeline_config_yaml(
            Conf.BASE_PATH / self._output_path / f"{self.pipeline_id}.config.yaml",
            param_dict_yaml)

        # name = self.pipeline_param.get("name")
        name = Path(Conf.BASE_PATH / self._output_path).name
        subject = self.pipeline_param.get("subject")
        shot_type = self.pipeline_param.get("shot_type")
        question_type = self.pipeline_param.get("question_type")
        metric_name = self.pipeline_param.get("metric_name")
        if not name or not subject or not shot_type:
            pipeline_logger.error(
                f"pipeline id: `{self.pipeline_id}` get result failed. `model name`,`subject`,`shot_type` has None.")
            return

        print(f"---------------{metric_name.name}---------------")
        result_file_path = run_get_result([name.replace("/", "-")], [subject], [shot_type], [self.pipeline_id],
                                          output_dir=Conf.BASE_PATH / self._output_path,
                                          classify_path="",
                                          cot=False,
                                          result_mark=f"{self.pipeline_id}",
                                          question_type=question_type,
                                          metric_name=metric_name)

        result_dict_yaml = yaml.load(json.dumps({"result_path": str(Conf.BASE_PATH / result_file_path)}),
                                     Loader=yaml.FullLoader)
        BaseEvaluationPipeline.__write_pipeline_config_yaml(
            Conf.BASE_PATH / self._output_path / f"{self.pipeline_id}.config.yaml",
            result_dict_yaml)

    def run_step_by_processes(self, *args, **kwargs):
        """ Run pipline template

        Use template model. Run all processes by step
        :param args: args
        :param kwargs: kwargs
        """
        self.__dry_run = self._pipeline_param.get("dry_run") if self._pipeline_param.get(
            "dry_run") is not None else False
        pipeline_logger.info(
            f"pipeline id: `{self.pipeline_id}` =============== Begin pipeline process ===============")
        if not self.__dry_run:
            self._pre_process_init_model_process(*args, **kwargs)
            self._init_model_process(*args, **kwargs)
            self._pre_process_session_generation_process(*args, **kwargs)
            self._session_generation_process(*args, **kwargs)
            self._pre_process_result_generation_process(*args, **kwargs)
            self._result_generation_process(*args, **kwargs)
            self._post_process_result_generation_process(*args, **kwargs)
        pipeline_logger.info(f"pipeline id: `{self.pipeline_id}` =============== End pipeline process ===============")

    @classmethod
    def __write_pipeline_config_yaml(cls, pipeline_config_yaml_path, yaml_content):
        with open(pipeline_config_yaml_path, "a", encoding="utf-8") as result_yaml:
            yaml.dump(data=yaml_content, stream=result_yaml, allow_unicode=True)
