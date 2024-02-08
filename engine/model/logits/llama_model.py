# -*- coding: utf-8 -*-
import torch as torch
from conf import ModelType
from .base_model import BaseModel


class LLamaModel(BaseModel):
    """ LLama Model

    """

    key_expression = ModelType.LLAMA.name

    def __init__(
            self,
            model_type: ModelType,
            model_name: str,
            *args,
            **kwargs):
        self.__model = None
        self.__tokenizer = None
        self.__auto_model_causalml_params = None
        self.__model_inference_params = None
        super().__init__(model_type,
                         model_name,
                         *args,
                         **kwargs)

    def pre_process_session_generator(self, *args, **kwargs):
        """ Preprocess session generator

        :param args: args
        :param kwargs: kwargs
        """
        if self.model_name.lower().split('-')[-1] == '65b':
            self.__auto_model_causalml_params = self.model_param.get("auto_model_causalml_params")
            self.__auto_model_causalml_params.update({'torch_dtype': torch.bfloat16})

    def session_generator(self, *args, **kwargs):
        """ Session generator

        :param args: args
        :param kwargs: kwargs
        """
        if not self.__auto_model_causalml_params:
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
            assert result.startswith(cot_prompt_text)
            answer = result[len(cot_prompt_text):]
            return answer

    def result_generator(self, prompt_text, *args, **kwargs):
        """ Result generator

        :param prompt_text: prompt text content
        :param args: args
        :param kwargs: kwargs e.g. max_new_tokens=10, batch_size=4
        """
        input_ids = None
        if BaseModel.is_exist_special_word_in_model_name(self.model_name.lower(), "chat"):
            messages = [
                {"role": "user", "content": prompt_text}
            ]
            formatted_conversation = self.__tokenizer.apply_chat_template(messages, tokenize=False)
            input_ids = self.__tokenizer(formatted_conversation, return_tensors="pt").input_ids
        return self.base_result_generator(prompt_text, self.__tokenizer, input_ids, *args, **kwargs)


