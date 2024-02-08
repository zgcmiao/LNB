# -*- coding: utf-8 -*-

from conf import Conf
from utils import BaseManager, pipeline_logger, CommonHelper
from model import ModelType, QuestionType
import importlib

module_path = 'evaluation_pipeline'


class PipelineManager(BaseManager):
    """ Pipeline manager

    Manage pipeline, provide version control of pipeline etc.
    """

    def __init__(self, version=("%s" % Conf.DEFAULT_VERSION), *args, **kwargs):
        """ Init manager

        :param version: version control of model
        """
        super().__init__(module_path, version)

    def get_pipeline_instance(self,
                              model_name: str,
                              model_type: ModelType,
                              pipeline_params: dict,
                              model_params: dict = None,
                              *args,
                              **kwargs):
        """ Get pipeline instance by version + model_type + param

        :param model_name: model name
        :param model_type: model type
        :param pipeline_params: model param
        :param model_params: model param
        :param args: args
        :param kwargs: kwargs
        """
        pipeline_logger.debug(f"loading the `{self._version}` pipeline module.")
        pipeline_module = importlib.import_module(f"{module_path}.{self._version}")
        pipeline_logger.debug(f"load the `{self._version}` pipeline module success.")
        # load model configuration params
        model_configuration = getattr(getattr(pipeline_module, "model_configuration_params"),
                                      "get_params_by_model_type")(model_type, model_name)
        if model_params:
            model_configuration.update(model_params)

        # filter base pipeline subclass
        base_pipeline = getattr(getattr(pipeline_module, "pipeline_base"), "BaseEvaluationPipeline")
        list_base_pipeline_subclass = []
        for attr in dir(pipeline_module):
            attr_object = getattr(pipeline_module, attr)
            if isinstance(attr_object, type) and issubclass(attr_object, base_pipeline):
                list_base_pipeline_subclass.append(attr_object)

        # dict key_expression: subclass
        dict_subclass_key_expression = {_.key_expression: _ for _ in list_base_pipeline_subclass if
                                        hasattr(_, "key_expression")}

        question_type = pipeline_params.get("question_type", "")
        # create pipeline instance by model type
        print(question_type)
        if model_type.name not in dict_subclass_key_expression and question_type.name not in dict_subclass_key_expression:
            pipeline = base_pipeline
        else:
            if model_type.name in dict_subclass_key_expression:
                pipeline = dict_subclass_key_expression[model_type.name]
            if question_type.name in dict_subclass_key_expression:
                pipeline = dict_subclass_key_expression[question_type.name]

        kwargs.update({
            "pipeline_param": pipeline_params,
            "model_param": model_configuration,
            "pipeline_id": CommonHelper.generate_uuid() if not pipeline_params or not pipeline_params.get(
                "pipeline_id") else pipeline_params.get("pipeline_id")
        })
        pipeline_instance = pipeline(model_type, model_name, args, **kwargs)
        return pipeline_instance


def _pipeline_uuid_generator():
    return f"pln-{CommonHelper.generate_uuid()}"


if __name__ == '__main__':
    from regex import GlmEvaluationPipeline

    assert PipelineManager(Conf.DEFAULT_VERSION).get_pipeline_instance("THDUM/glm-10b", ModelType.GLM,
                                                                       None).key_expression \
           == GlmEvaluationPipeline.key_expression
