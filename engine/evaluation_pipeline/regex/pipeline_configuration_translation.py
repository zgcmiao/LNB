# -*- coding: utf-8 -*-
import json
import yaml
from pathlib import Path
from tqdm import tqdm

from conf import QuestionType, ModelType, Conf, error_code
from evaluation_pipeline.regex import BaseEvaluationPipeline
from evaluation_pipeline.regex.pipeline_helper import dict_input_output_file_path_mapper, ParametersEncoder
from model import ModelManager
from script import cal_trans_precision_recall, compute_score_line_level, compute_score_block_level
from utils import pipeline_logger, CommonHelper
from utils.decorator import pipeline_logger_wrapper

CONFIGURE_TRANSLATION = "network_configure_translation"

OVERVIEW_RESULT_JSON_FILE = "overview_result.json"


class ConfigurationTranslationPipeline(BaseEvaluationPipeline):
    """ Evaluation pipeline

    """

    key_expression = QuestionType.CONFIGURATION_TRANSLATION.name

    def __init__(self,
                 model_type: ModelType,
                 model_name: str,
                 *args,
                 **kwargs):
        """Init EvaluationPiplineBase class

                :param model_type: model type, e.g. LLAMA
                :param model_name: model name, e.g. llama-7b
                """
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
        self._overview_result_path = Path(self._output_path).parent
        name = Path(Conf.BASE_PATH / self._output_path).name
        for id, exam_title, exam_questions, output_path, total_num in self.yield_questions_from_input_files(
                self._dict_mapper):
            is_exist, path = CommonHelper.judge_file_or_dir_exist(Conf.BASE_PATH / output_path)
            if not is_exist:
                CommonHelper.create_file(path)
            self.save_to_overview_result(exam_title, name, total_num)
            for question in tqdm(exam_questions):
                item_id = question['id']
                item_title = question['title']
                item_prompt_text = self._model_instance.request_prompt_generator(item_content=question,
                                                                                 prompt_generator_func=self.__prompt_generator_func)
                self.__prompt_text = item_prompt_text
                item_result = self._model_instance.result_generator(prompt_text=self.__prompt_text)
                print("\n--------PROMPT--------\n" + self.__prompt_text)
                print("\n--------ANSWER--------\n" + item_result)

                with open(path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(
                        {'id': item_id, 'title': item_title, 'prompt': item_prompt_text, 'answer': item_result},
                        ensure_ascii=False) + '\n')

            self. _output_full_path = path
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
        output_full_path = self._output_full_path
        input_file_or_directory_path_ = self._pipeline_param.get("input_file_or_directory_path")

        param_dict = {}
        param_dict.update({"pipeline_param": self.pipeline_param})
        param_dict.update({"model_param": self.model_param})
        param_dict_json_str = json.dumps(param_dict, cls=ParametersEncoder)
        param_dict_yaml = yaml.load(param_dict_json_str, Loader=yaml.FullLoader)

        ConfigurationTranslationPipeline.__write_pipeline_config_yaml(
            Conf.BASE_PATH / self._output_path / f"{self.pipeline_id}.config.yaml",
            param_dict_yaml)

        line_precision, line_recall, line_f1 = cal_trans_precision_recall(input_file_or_directory_path_,
                                                                          output_full_path, compute_score_line_level)
        block_precision, block_recall, block_f1 = cal_trans_precision_recall(input_file_or_directory_path_,
                                                                             output_full_path,
                                                                             compute_score_block_level)
        result_file_path = Conf.BASE_PATH / self._output_path / f"{self.pipeline_id}_result.json"
        with open(result_file_path, "w") as f_out:
            f_out.write(json.dumps({"line_precision": line_precision, "line_recall": line_recall, "line_f1": line_f1,
                                    "block_precision": block_precision, "block_recall": block_recall,
                                    "block_f1": block_f1}, ensure_ascii=False, indent=4))

        result_dict_yaml = yaml.load(json.dumps({"result_path": str(Conf.BASE_PATH / result_file_path)}),
                                     Loader=yaml.FullLoader)
        ConfigurationTranslationPipeline.__write_pipeline_config_yaml(
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

    def yield_questions_from_input_files(self, input_output_mapper):
        for input_path, output_path in input_output_mapper.items():
            output_path = output_path.parent / f"{self._pipeline_id}.auto.{output_path.name[:output_path.name.find('.')]}-zero-shot.json"
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                id = CONFIGURE_TRANSLATION
                title = CONFIGURE_TRANSLATION
                yield id, title, data, output_path, len(data)
