# -*- coding: utf-8 -*-
from conf import error_code, ModelType
from .base_model import BaseModel

DEVICE = "device"
DEVICE_MAP = "device_map"
GENERATED_TEXT_KEY = 'generated_text'


class FalconModel(BaseModel):
    """ Falcon Model

    """

    key_expression = ModelType.FALCON.name

    def __init__(
            self,
            model_type: ModelType,
            model_name: str,
            *args,
            **kwargs):
        self.__model = None
        self.__tokenizer = None
        self.__model_pipeline_params = None
        self.__model_inference_params = None
        super().__init__(model_type,
                         model_name,
                         *args,
                         **kwargs)

        self.__model_pipeline_params = self.model_param.get("model_pipeline_params")
        # support finetune model, `model` is a finetune directory.
        self._model_name = self.__model_pipeline_params.pop("model") if "model" in self.__model_pipeline_params else self.model_name

    def pre_process_session_generator(self, *args, **kwargs):
        """ Preprocess session generator

        :param args: args
        :param kwargs: kwargs
        """
        self.__tokenizer = self.tokenizer_factory(self.model_name)

    def session_generator(self, *args, **kwargs):
        """ Session generator

        Generate model session
        :param args: args
        :param kwargs: kwargs
        :return: session
        """
        self.__model_pipeline_params = self.model_param.get("model_pipeline_params")
        if not self.__model_pipeline_params:
            raise error_code.ParameterError(
                f"There is an exception in the `{self.model_name}` session generation process, and the parameter `model_pipeline_params` is missing.")

        self.__model = self.model_factory()
        self._model_session = self.transformers.pipeline(
            model=self.__model,
            tokenizer=self.__tokenizer,
            **self.__model_pipeline_params
        )

    def result_generator(self, prompt_text, *args, **kwargs):
        """ Result generator

        Generate model result
        :param prompt_text: prompt text content
        :param args: args
        :param kwargs: kwargs
        """
        self.__model_inference_params = self.model_param.get("model_inference_params")
        self.__model_inference_params.update({"eos_token_id": self.__tokenizer.eos_token_id})
        self.__model_inference_params.update(kwargs)

        result = self.model_session(prompt_text, **self.__model_inference_params)
        response = result[0]['%s' % GENERATED_TEXT_KEY]
        assert response.startswith(prompt_text)
        answer = response[len(prompt_text):]
        return answer
