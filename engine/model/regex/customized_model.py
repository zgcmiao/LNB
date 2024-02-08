# -*- coding: utf-8 -*-
import importlib
import os

from conf import error_code, ModelType
from .base_model import BaseModel

DEVICE = "device"
DEVICE_MAP = "device_map"
LOGGER_PREFIX = "CustomizedModel"


class CustomizedModel(BaseModel):
    """ Customized Model

    """

    key_expression = ModelType.CUSTOMIZED.name

    def __init__(
            self,
            model_type: ModelType,
            model_name: str,
            *args,
            **kwargs):
        self.__model = None
        self.__tokenizer = None
        self.__prompt_text = None
        self.__prompt_generator_func = None
        self.__customized_model_package = None
        self.__model_pipeline_params = None
        self.__model_inference_params = None
        super().__init__(model_type,
                         model_name,
                         *args,
                         **kwargs)

    def pre_process_session_generator(self, *args, **kwargs):
        """ Preprocess session generator
            get customized model from customized_model_package

        :param args: args
        :param kwargs: kwargs
        """
        self.__customized_model_package = self._model_param.get('customized_model_package')
        if self.__customized_model_package is None or not os.path.isfile(self.__customized_model_package):
            raise error_code.ParameterError(f'There is an exception in the `{self.model_name}` pre_process session '
                                            f'generator, and the parameter `customized_model_package` is missing or '
                                            f'not a file`.')

    def session_generator(self, *args, **kwargs):
        """ Session generator

        :param args: args
        :param kwargs: kwargs
        """
        from langchain_core.language_models import LLM
        spec = importlib.util.spec_from_file_location('customized_model', self.__customized_model_package)
        models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models)

        customized_model = None
        for attr in dir(models):
            attr_object = getattr(models, attr)
            if isinstance(attr_object, type) and issubclass(attr_object, LLM) and attr != 'LLM':
                customized_model = attr_object
                break
        if customized_model is None:
            raise error_code.ParameterError(f'There is an exception in load customized_model, no class is a subclass'
                                            f' of langchain_core.language_models.LLM.')
        self.__model_pipeline_params = self.model_param.get("model_pipeline_params", {})
        self._model_session = customized_model(**self.__model_pipeline_params)

    def result_generator(self, prompt_text, *args, **kwargs):
        """ Result generator

        :param prompt_text: prompt text content
        :param args: args
        :param kwargs: kwargs e.g. max_new_tokens=10, batch_size=4
        """
        self.__model_inference_params = self.model_param.get("model_inference_params", {})
        self.__model_inference_params.update(kwargs)

        result = self._model_session(prompt_text, **self.__model_inference_params)
        return result
