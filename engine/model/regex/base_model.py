# -*- coding: utf-8 -*-
import abc
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

    @classmethod
    def default_prompt_generator_func(
            cls, item_content, *args, **kwargs) -> str:
        """ Default prompt generator func

        :param item_content: item content
        :param args: args
        :param kwargs: kwargs
        :return: prompt text
        """
        content = ""
        choice = {}
        my_dict = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
            5: 'F',
            6: 'G',
            7: 'H',
            8: 'I',
            9: 'J',
            10: 'K'
        }

        content = "Question:"
        content += item_content['content']
        i = 0
        content += "Choices:"
        for choice in item_content['choices']:
            content += my_dict[i]
            content += ": "
            content += choice['content']
            content += ";"
            i += 1
        content += "You answer in the form of one or two letter representing the choice. "
        content += "The answer is: "
        print(content)
        return content

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
