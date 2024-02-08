# -*- coding: utf-8 -*-
import abc

from model import ModelType


class BaseEvaluationPipelineAbstract(metaclass=abc.ABCMeta):
    """ Evaluation pipeline base abstract

    """

    def __init__(self,
                 model_type: ModelType,
                 model_name: str,
                 *args,
                 **kwargs):
        """Init BaseEvaluationPipelineAbstract class

                :param model_type: model type, e.g. LLAMA
                :param model_name: model name, e.g. llama-7b
                """
        self._model_session = None
        self._model_type = model_type
        self._model_name = model_name
        self._pipeline_param = kwargs.get("pipeline_param")
        self._model_param = kwargs.get("model_param")
        self._pipeline_id = kwargs.get("pipeline_id")

    @abc.abstractmethod
    def _pre_process_init_model_process(self, *args, **kwargs):
        """ Process: Pre init evaluation model process

        Pre-process init evaluation model
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @abc.abstractmethod
    def _init_model_process(self, *args, **kwargs):
        """ Process: Init evaluation model process

        Init evaluation model
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @abc.abstractmethod
    def _pre_process_session_generation_process(self, *args, **kwargs):
        """ Process: Pre process session generation process

        Pre-process generate model session
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @abc.abstractmethod
    def _session_generation_process(self, *args, **kwargs):
        """ Process: Session generation process

        Generate model session
        :param args: args
        :param kwargs: kwargs
        :return: session
        """
        pass

    @abc.abstractmethod
    def _pre_process_result_generation_process(self, *args, **kwargs):
        """ Process: Pre process result generation process

        Pre-process generate model result
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @abc.abstractmethod
    def _result_generation_process(self, *args, **kwargs):
        """ Process: Result generation process

        Generate model result
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @abc.abstractmethod
    def _post_process_result_generation_process(self, *args, **kwargs):
        """ Process: Post process result generation process

        Pre-post generate model result
        :param args: args
        :param kwargs: kwargs
        """
        pass

    @property
    def model_type(self):
        return self._model_type

    @property
    def model_name(self):
        return self._model_name

    @property
    def pipeline_id(self):
        return self._pipeline_id

    @property
    def model_param(self):
        return self._model_param

    @property
    def pipeline_param(self):
        return self._pipeline_param
