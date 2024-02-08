# -*- coding: utf-8 -*-
import abc
from pathlib import Path

import numpy as np
import torch
from conf import ModelType, TransformersLocalRemoteType
from model.regex.model_helper import transformers_factory


class BaseModel(metaclass=abc.ABCMeta):
    """ Base Model class

    The base model clss contains common operations and methods for models.
    """

    def __init__(
            self,
            model_type: ModelType,
            model_name: str,
            *args,
            **kwargs):
        """Init BaseModel class

        :param model_type: model type, e.g. LLAMA
        :param model_name: model name, e.g. llama-7b
        """
        self._prompt_text = None
        self._model_session = None
        self._model_type = model_type
        self._model_name = model_name
        self._model_param = kwargs

        # `enable_local_transformers` is TRUE， use LOCAL Transformers package. otherwise use REMOTE
        if self._model_param.get("enable_local_transformers", False):
            self.__transformers = transformers_factory(self._model_type, TransformersLocalRemoteType.LOCAL)
            self.__enable_local_transformers = True
        else:
            self.__transformers = transformers_factory(self._model_type, TransformersLocalRemoteType.REMOTE)
            self.__enable_local_transformers = False

    @abc.abstractmethod
    def pre_process_session_generator(self, *args, **kwargs):
        """ Preprocess session generator

        :param args: args
        :param kwargs: kwargs
        """

    @abc.abstractmethod
    def session_generator(self, *args, **kwargs):
        """ Session generator

        Generate model session
        :param args: args
        :param kwargs: kwargs
        :return: session
        """
        pass

    @abc.abstractmethod
    def pre_result_generator(self, *args, **kwargs):
        """ Result generator

        Generate model result
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @abc.abstractmethod
    def result_generator(self, *args, **kwargs):
        """ Result generator

        Generate model result
        :param args: args
        :param kwargs: kwargs
        """
        pass

    def __describe_configuration(self):
        """ Describe model configuration

        :return: configuration
        """
        __configuration_desc = {
            "model_type": self.__model_type,
            "model_name": self.__model_name,
            "model_param": self.__model_param
        }
        return __configuration_desc

    def request_prompt_generator(
            self,
            item_content,
            prompt_generator_func=None):
        """ Generator request prompt

        :param item_content: item e.g. question content
        :param prompt_generator_func: prompt generator function
        :return: prompt text
        """
        if prompt_generator_func is None:
            prompt_generator_func = BaseModel.default_prompt_generator_func

        prompt_text = prompt_generator_func(item_content=item_content)
        return prompt_text

    @property
    def model_name(self):
        return self._model_name

    @property
    def model_type(self):
        return self._model_type

    @property
    def model_session(self):
        return self._model_session

    @property
    def model_param(self):
        return self._model_param

    @property
    def prompt_text(self):
        return self._prompt_text

    @property
    def transformers(self):
        return self.__transformers

    @property
    def enable_local_transformers(self):
        return self.__enable_local_transformers

    def __merge_weights_to_model(self, model_name_or_path: str, weights_path: str):
        model = self.transformers.AutoModelForCausalLM.from_pretrained(model_name_or_path, load_in_8bit=False,
                                                                       torch_dtype=torch.float16,
                                                                       device_map="auto", trust_remote_code=True)
        from peft import PeftModel
        peft_model = PeftModel.from_pretrained(model, weights_path, torch_dtype=torch.float16)
        return peft_model.merge_and_unload()

    def model_factory(self):
        """ Get model based on ordered conditions

        Default case:
            Use raw model name or path
        case 2:
            Configure parameters in model_pipeline_params.
        case 3:
            Specify special finetune_weights.
            - need_merge_weights is False
                set finetune_weights path to model
            - need_merge_weights is True
                merge weights to model

        """
        model_ = self.model_name
        if self.model_param.get("model_pipeline_params", {}).get("model", ""):
            model_ = self.model_param.get("model_pipeline_params", {}).pop("model")
        if self.model_param.get("finetune_weights", ""):
            if self.model_param.get("need_merge_weights", False):
                model_ = self.__merge_weights_to_model(self.model_name, self.model_param.get("finetune_weights"))
            else:
                model_ = self.model_param.get("finetune_weights")
        return model_

    def tokenizer_factory(self, model_name):
        """ Get tokenizer

        Default case:
            Get tokenizer by default parameters
        case 2:
            Get tokenizer by model_tokenizer_params parameters {@link model_configuration_params.py}

        """
        if bool(self.model_param.get("model_tokenizer_params", {})):
            tokenizer_ = self.transformers.AutoTokenizer.from_pretrained(model_name, **self.model_param.get(
                "model_tokenizer_params"))
        else:
            tokenizer_ = self.transformers.AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        return tokenizer_

    @staticmethod
    def is_exist_special_word_in_model_name(model_name, special_word):
        # if model_name is a path
        model_name_path = Path(model_name)
        if Path.exists(model_name_path):
            return True if special_word in model_name_path.name else False
        # model_name is only name
        else:
            return True if special_word in model_name else False

    def base_result_generator(self, prompt_text, tokenizer, input_ids, *args, **kwargs):
        if input_ids is None:
            if not prompt_text:
                raise ValueError("please specify at least one parameter input_ids or prompt_text.");
            input_ids = tokenizer(prompt_text, return_tensors="pt").input_ids.cuda()

        logits = self._model_session(input_ids).logits[:, -1].flatten()

        list_default_choices = ["A", "B", "C", "D"]
        list_choices = kwargs.get("list_choices", list_default_choices)
        probs = (
            torch.nn.functional.softmax(
                torch.tensor(
                    [logits[tokenizer(choice, add_special_tokens=False).input_ids[-1]] for choice in list_choices]
                ),
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
