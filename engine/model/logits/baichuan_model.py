# -*- coding: utf-8 -*-
from conf import ModelType
from .base_model import BaseModel


class BaichuanModel(BaseModel):
    """ Baichuan Model

    """

    key_expression = ModelType.BAICHUAN.name

    def __init__(
            self,
            model_type: ModelType,
            model_name: str,
            *args,
            **kwargs):
        self.__model = None
        self.__tokenizer = None
        self.__auto_model_causalml_params = None
        super().__init__(model_type,
                         model_name,
                         *args,
                         **kwargs)

    def pre_process_session_generator(self, *args, **kwargs):
        """ Preprocess session generator

        :param args: args
        :param kwargs: kwargs
        """
        pass

    def session_generator(self, *args, **kwargs):
        """ Session generator

        :param args: args
        :param kwargs: kwargs
        """
        self.__auto_model_causalml_params = self.model_param.get("auto_model_causalml_params")
        self.__model = self.model_factory()
        self.__tokenizer = self.tokenizer_factory(self.model_name)
        self._model_session = self.transformers.AutoModelForCausalLM.from_pretrained(
            self.__model,
            **self.__auto_model_causalml_params
        )

    def pre_result_generator(self, *args, **kwargs):
        """ Pre result generator

        :param args: args
        :param kwargs: kwargs
        """
        _pre_gen_explanation_for_inference_flag = kwargs.get("pre_gen_explanation_for_inference_flag")
        if _pre_gen_explanation_for_inference_flag:
            self.__model_inference_params = self.model_param.get("model_inference_params")
            _max_new_tokens = self.__model_inference_params.get("max_new_tokens", 20)

            cot_prompt_text = kwargs.get("cot_prompt_text")
            cot_prompt_input_ids = self.__tokenizer(cot_prompt_text, return_tensors="pt")
            result = self._model_session.generate(**cot_prompt_input_ids, max_new_tokens=_max_new_tokens)
            result = self.__tokenizer.decode(result[0], skip_special_tokens=True)
            if not result.startswith(cot_prompt_text):
                return ""
            answer = result[len(cot_prompt_text):]
            return answer

    def result_generator(self, prompt_text, *args, **kwargs):
        """ Result generator

        :param prompt_text: prompt text content
        :param args: args
        :param kwargs: kwargs e.g. max_new_tokens=10, batch_size=4
        """
        return self.base_result_generator(prompt_text, self.__tokenizer, None, *args, **kwargs)
