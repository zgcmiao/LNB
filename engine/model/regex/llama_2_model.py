# -*- coding: utf-8 -*-
import torch as torch

from conf import error_code, ModelType
from .base_model import BaseModel

DEVICE = "device"
DEVICE_MAP = "device_map"
GENERATED_TEXT_KEY = 'generated_text'
LOGGER_PREFIX = "LLamaModel"


class LLama2Model(BaseModel):
    """ LLama2 Model

    """

    key_expression = ModelType.LLAMA2.name

    def __init__(
            self,
            model_type: ModelType,
            model_name: str,
            *args,
            **kwargs):
        self.__model = None
        self.__tokenizer = None
        self.__prompt_text = None
        self.__model_pipeline_params = None
        self.__model_inference_params = None
        self.__prompt_generator_func = None
        super().__init__(model_type,
                         model_name,
                         *args,
                         **kwargs)

    def pre_process_session_generator(self, *args, **kwargs):
        """ Preprocess session generator

        :param args: args
        :param kwargs: kwargs
        """
        self.__model_pipeline_params = self.model_param.get("model_pipeline_params")
        if self.model_name.lower().split('-')[-1] == '65b':
            self.__model_pipeline_params.update({'torch_dtype': torch.bfloat16})
        if kwargs.get("prompt_generator_func", False) and self.enable_local_transformers:
            self.__prompt_generator_func = kwargs.get("prompt_generator_func")
            self.__model_pipeline_params.update({"prompt_prefix": self.__prompt_generator_func()})
        else:
            self.__model_pipeline_params.pop("cache_prompt_prefix")

    def session_generator(self, *args, **kwargs):
        """ Session generator

        :param args: args
        :param kwargs: kwargs
        """
        self.__model_pipeline_params = self.model_param.get("model_pipeline_params")
        if not self.__model_pipeline_params:
            raise error_code.ParameterError(
                f"There is an exception in the `{self.model_name}` session generation process, and the parameter `model_pipeline_params` is missing.")

        self.__model = self.model_factory()
        self.__tokenizer = self.tokenizer_factory(self.model_name)
        self._model_session = self.transformers.pipeline(model=self.__model,
                                                         tokenizer=self.__tokenizer,
                                                         **self.__model_pipeline_params)

    def result_generator(self, prompt_text, *args, **kwargs):
        """ Result generator

        :param prompt_text: prompt text content
        :param args: args
        :param kwargs: kwargs e.g. max_new_tokens=10, batch_size=4
        """
        self.__model_inference_params = self.model_param.get("model_inference_params")
        self.__model_inference_params.update(kwargs)

        result = self.model_session(prompt_text, **self.__model_inference_params)
        resp = result[0][('%s' % GENERATED_TEXT_KEY)]
        assert resp.startswith(prompt_text)
        answer = resp[len(prompt_text):]
        return answer
