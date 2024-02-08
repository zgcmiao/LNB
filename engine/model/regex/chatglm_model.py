# -*- coding: utf-8 -*-
from conf import error_code, ModelType
from .base_model import BaseModel


class ChatGLMModel(BaseModel):
    """ ChatGLM Model

    """

    key_expression = ModelType.CHATGLM.name

    def __init__(
            self,
            model_type: ModelType,
            model_name: str,
            *args,
            **kwargs):
        self.__model = None
        self.__tokenizer = None
        self.__auto_model_params = None
        self.__model_tokenizer_params = None
        super().__init__(model_type,
                         model_name,
                         *args,
                         **kwargs)

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
        self.__auto_model_params = self.model_param.get("auto_model_params")
        if not self.__auto_model_params:
            raise error_code.ParameterError(
                f"There is an exception in the `{self.model_name}` session generation process, and the parameter `auto_model_params` is missing.")
        self.__model = self.model_factory()
        self._model_session = self.transformers.AutoModel.from_pretrained(self.__model,
                                                                          **self.__auto_model_params).half().cuda()

    def result_generator(self, prompt_text, *args, **kwargs):
        """ Result generator

        Generate model result
        :param prompt_text: prompt text content
        :param args: args
        :param kwargs: kwargs
        """
        response, history = self._model_session.chat(self.__tokenizer,
                                                     prompt_text,
                                                     history=[])
        return response
