import abc
import inspect
import sys
from conf import MetricName, Conf
from script.helper.script_helper import is_contain_chinese, read_sys_env
from utils import pipeline_logger
# import system variables needs to be before the evaluate module
read_sys_env(Conf.ENV_LIST)
import evaluate


class BaseMetric(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        self._metric_result = None
        self._metric_name = None

    def evaluate(self, predict, label):
        raise NotImplementedError

    @property
    def metric_result(self):
        return self._metric_result

    @classmethod
    def metric_name(cls):
        pass


class ExactMatchMetric(BaseMetric):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def metric_name(cls):
        return MetricName.Exact

    def evaluate(self, predict, label):
        if predict and label and predict.lower() == label.lower():
            self._metric_result = 1
        else:
            self._metric_result = 0


class BleuMetric(BaseMetric):
    def __init__(self, *args, **kwargs):
        self.metric_model = evaluate.load('bleu')
        super().__init__(*args, **kwargs)

    @classmethod
    def metric_name(cls):
        return MetricName.Bleu

    def _preprocess(self, predict, label):
        """
        Preprocess the data and manually add spaces to Chinese words for word segmentation.
        """
        has_chinese_character = False
        if is_contain_chinese(predict) or is_contain_chinese(label):
            has_chinese_character = True

        if has_chinese_character:
            import spacy
            nlp = spacy.load("zh_core_web_sm")
            predict = list(nlp(predict))
            predict = [str(s) for s in predict]
            predict = ' '.join(predict)
            label = list(nlp(label))
            label = [str(s) for s in label]
            label = ' '.join(label)
        return predict, label

    def evaluate(self, predict, label):
        predict, label = self._preprocess(predict, label)
        predictions = [f"{predict}"]
        references = [
            [f"{label}"]
        ]
        try:
            results = self.metric_model.compute(predictions=predictions, references=references)
            reference_length = results.get("reference_length", 0)
            if reference_length >= 4:
                result = sum(results.get("precisions", [])) / 4
            else:
                result = sum(results.get("precisions", [])[0: reference_length]) / reference_length if reference_length != 0 else 0
        except Exception as ex:
            pipeline_logger.error(f'BleuMetric | error while evaluate, exception: {repr(ex)}')
            result = 0
        self._metric_result = result
        pipeline_logger.info(f'BleuMetric result: {self._metric_result}')


class RougeMetric(BaseMetric):
    def __init__(self, *args, **kwargs):
        self.metric_model = evaluate.load('rouge')
        super().__init__(*args, **kwargs)

    @classmethod
    def metric_name(cls):
        return MetricName.Rouge

    def _preprocess(self, predict, label):
        """
        Preprocess the data and manually add spaces to Chinese words for word segmentation.
        """
        has_chinese_character = False
        if is_contain_chinese(predict) or is_contain_chinese(label):
            has_chinese_character = True

        if has_chinese_character:
            import spacy
            nlp = spacy.load("zh_core_web_sm")
            predict = list(nlp(predict))
            predict = [str(s) for s in predict]
            predict = ' '.join(predict)
            label = list(nlp(label))
            label = [str(s) for s in label]
            label = ' '.join(label)
        return predict, label

    def evaluate(self, predict, label):
        predict, label = self._preprocess(predict, label)
        predictions = [f"{predict}"]
        references = [
            [f"{label}"]
        ]
        try:
            results = self.metric_model.compute(predictions=predictions, references=references)
            reference_length = len(predict.split(" "))
            if reference_length >= 4:
                result = sum(list(results.values())) / 4
            else:
                result = (sum(list(results.values())[0: reference_length]) / reference_length) if reference_length != 0 else 0
        except Exception as ex:
            pipeline_logger.error(f'RougeMetric | error while evaluate, exception: {repr(ex)}')
            result = 0
        self._metric_result = result
        pipeline_logger.info(f'RougeMetric result: {self._metric_result}')


class MetricStrategy:
    def __init__(self, metric_name):
        self.__strategy = None
        self._get_strategy(metric_name)

    def _get_strategy(self, metric_name: MetricName):
        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if issubclass(cls, BaseMetric) and cls.metric_name() == metric_name:
                self.__strategy = cls()
        if self.__strategy is None:
            raise ValueError("please specify the question type in the `MetricName` enum class.")

    def evaluate(self, predict, label):
        self.__strategy.evaluate(predict, label)

    def metric_result(self):
        return self.__strategy.metric_result
