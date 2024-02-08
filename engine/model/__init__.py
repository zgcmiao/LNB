# -*- coding: utf-8 -*-
import importlib

from conf import Conf, error_code, ModelType, QuestionType
from utils import BaseManager, pipeline_logger

module_path = 'model'


def _list_subclass_from_base_class() -> list:
    """ List subclasses that inherit the base class

    """
    pass


def _list_subclass_key_expression(list_subclass: [list]) -> list:
    """ List subclasses key_expression

    """
    pass


class ModelManager(BaseManager):
    """ Model manager

    Manage model, provide version control of model, model information, etc.
    """

    def __init__(self, version=("%s" % Conf.DEFAULT_VERSION), *args, **kwargs):
        """ Init manager

        :param version: version control of model
        """
        super().__init__(module_path, version)

    def get_model_instance(self, model_type: ModelType, model_name: str, *args, **model_param: dict):
        """ Get model instance by version + model_name + param

        :param model_type: model type
        :param model_name: model name
        :param args: args
        :param kwargs: kwargs
        """
        pipeline_logger.debug(f"loading the `{self._version}` model module.")
        # import module by version
        model_module = importlib.import_module(f"{module_path}.{self._version}")
        pipeline_logger.debug(f"load the `{self._version}` model module success.")
        # filter base model subclass
        base_model = getattr(getattr(model_module, "base_model"), "BaseModel")
        list_base_model_subclass = []
        for attr in dir(model_module):
            attr_object = getattr(model_module, attr)
            if isinstance(attr_object, type) and issubclass(attr_object, base_model):
                list_base_model_subclass.append(attr_object)
        # dict key_expression: subclass
        dict_subclass_key_expression = {_.key_expression: _ for _ in list_base_model_subclass}
        # create model instance by model type
        if model_type.name not in dict_subclass_key_expression:
            error_message = f"The specified model type `{model_type.name}` under the {self._version} module does not exist."
            raise error_code.ParameterError(error_message)
        model_ = dict_subclass_key_expression[model_type.name]
        model_instance = model_(model_type, model_name, *args, **model_param)
        return model_instance


if __name__ == '__main__':
    from regex.llama_model import LLamaModel
    from regex.baichuan_model import BaichuanModel
    from regex.chatglm_model import ChatGLMModel
    from regex.falcon_model import FalconModel

    assert isinstance(
        ModelManager(Conf.DEFAULT_VERSION).get_model_instance("huggyllama/llama-7b", ModelType.LLAMA),
        LLamaModel
    )
    assert isinstance(
        ModelManager(Conf.DEFAULT_VERSION).get_model_instance("baichuan-inc/baichuan-7B", ModelType.BAICHUAN),
        BaichuanModel
    )
    assert isinstance(
        ModelManager(Conf.DEFAULT_VERSION).get_model_instance("THUDM/chatglm2-6b", ModelType.CHATGLM),
        ChatGLMModel
    )
    assert isinstance(
        ModelManager(Conf.DEFAULT_VERSION).get_model_instance("tiiuae/falcon-40b", ModelType.FALCON),
        FalconModel
    )
