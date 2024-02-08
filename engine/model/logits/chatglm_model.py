# -*- coding: utf-8 -*-
import numpy as np
import torch
from conf import ModelType
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
        self._model_session = self.transformers.AutoModel.from_pretrained(
            self.__model, **self.__auto_model_causalml_params).half().cuda()

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
            answer, history = self._model_session.chat(self.__tokenizer,
                                                       cot_prompt_text,
                                                       history=[])
            return answer

    def result_generator(self, prompt_text, *args, **kwargs):
        """ Result generator

        :param prompt_text: prompt text content
        :param args: args
        :param kwargs: kwargs e.g. max_new_tokens=10, batch_size=4
        """
        prompt_text = f"[Round 0]\n问：{prompt_text}\n答："
        input_ids = self.__tokenizer([prompt_text], return_tensors="pt").to(self._model_session.device)['input_ids']
        logits = self._model_session(input_ids).logits[:, -1].flatten()
        list_default_choices = ["A", "B", "C", "D"]
        list_choices = kwargs.get("list_choices", list_default_choices)
        probs = (
            torch.nn.functional.softmax(
                torch.tensor(
                    [logits[self.__tokenizer(choice, add_special_tokens=False).input_ids[-1]] for choice in list_choices]
                ).float(),
                dim=0,
            )
            .detach()
            .cpu()
            .to(torch.float32)
            .numpy()
        )
        answer = {0: "A", 1: "B", 2: "C", 3: "D"}[np.argmax(probs)]
        prediction_dict = {_[0]: _[1] for _ in zip(list_default_choices, probs.tolist())}
        return answer, prediction_dict
