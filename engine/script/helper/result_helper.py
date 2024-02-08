import abc
import inspect
import json
import re
import string
import sys

from script import get_answer
from conf import ResultDataFileType, QuestionType
from utils import pipeline_logger


class BaseResult(metaclass=abc.ABCMeta):
    def __init__(self, question_type):
        self._list_answer = None
        self._question_type = question_type

    def load_result_data(self, output_path, cot):
        raise NotImplementedError

    def _raw_answer_parsing(self, raw_answer, exam_id=None, cot=False):
        def _question_key(id, title):
            return f"{id}_{title}"
        answer_key = None
        if raw_answer.get("id"):
            answer_key = _question_key(raw_answer.get("id"), raw_answer.get("title"))
        elif exam_id:
            answer_key = _question_key(exam_id, raw_answer.get("title"))
        if not answer_key:
            raise ValueError("answer_key error occurred.")

        ans = raw_answer.get("answer")
        if self._question_type in [QuestionType.MULTIPLE_CHOICE]:
            if ans.startswith('The following are multiple choice questions'):
                matches = re.findall(r'Answer: ([A-Z])', ans)
                ans = matches[-1] if matches else ''
            else:
                ans = ans.splitlines()[0].strip() if ans else ''
                if ans != '' and ans not in string.ascii_uppercase:
                    ans = get_answer(raw_answer.get("answer").strip(), cot)
                    ans = ''.join(ans)
                elif ans == '':
                    ans = get_answer(raw_answer.get("answer").strip(), cot)
                    ans = ''.join(ans)
        elif self._question_type in [QuestionType.CLOZE]:
            ans = ans.splitlines()[0].strip() if ans else ''
        elif self._question_type in [QuestionType.QUESTION_AND_ANSWER]:
            ans = ans.splitlines()[0].strip() if ans else ''
        return answer_key, ans

    @property
    def list_answer(self):
        return self._list_answer

    @classmethod
    def result_file_type(cls):
        pass


class NormalJsonResult(BaseResult):
    """
    Normal json Result.
    file_type: json
    data_struct: {"id": "xxx", "title", “answers": [{"id": "xxx", "title": "xxx", "answer": "xxx"}]}
    """
    def __init__(self, question_type):
        super().__init__(question_type)

    @classmethod
    def result_file_type(cls):
        return ResultDataFileType.NormalJson

    def load_result_data(self, answer_file, cot):
        pipeline_logger.info(f'NormalJsonResult | begin load result data from {answer_file}...')
        with open(answer_file, 'r', encoding='utf-8', errors='ignore') as f:
            answer_json = json.load(f)
        exam_id = answer_json["id"]
        list_answers = {}
        for answer in answer_json["answers"]:
            answer_key, answer_parsed = self._raw_answer_parsing(answer, exam_id, cot)
            list_answers.update({answer_key: {'answer': answer_parsed, 'raw_answer': answer.get('answer')}})
        pipeline_logger.info('')
        self._list_answer = list_answers
        pipeline_logger.info(f'NormalJsonResult | load result data from {answer_file} end, '
                             f'total {len(self._list_answer)} answers.')


class TextResult(BaseResult):
    def __init__(self, question_type):
        super().__init__(question_type)

    @classmethod
    def result_file_type(cls):
        return ResultDataFileType.Text

    def load_result_data(self, answer_file, cot):
        pipeline_logger.info(f'TextResult | begin load result data from {answer_file}...')
        list_answer = []
        with open(answer_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    line_dict = eval(line.replace('\n', '').strip())
                    list_answer.append(line_dict)
                except Exception as ex:
                    pipeline_logger.error(f'TextResult | line: {line}')
                    try:
                        line_dict = json.loads(line.replace('\n', '').strip())
                        if line_dict['answer'] is None:
                            line_dict['answer'] = ''
                        list_answer.append(line_dict)
                    except Exception as ex:
                        pipeline_logger.error(
                            f'TextResult | error in load_result_data {answer_file}, exception: {repr(ex)}')
                        continue
                    continue
        list_answers = {}
        for answer in list_answer:
            answer_key, answer_parsed = self._raw_answer_parsing(answer, cot=cot)
            list_answers.update({answer_key: {'answer': answer_parsed, 'raw_answer': answer.get('answer')}})
        self._list_answer = list_answers
        pipeline_logger.info(f'TextResult | load result data from {answer_file} end, '
                             f'total {len(self._list_answer)} answers.')


class GlmJsonResult(BaseResult):
    def __init__(self, question_type):
        super().__init__(question_type)

    @classmethod
    def result_file_type(cls):
        return ResultDataFileType.GlmJson

    def load_result_data(self, answer_file, cot):
        pipeline_logger.info(f'GlmJsonResult | begin load result data from {answer_file}...')
        with open(answer_file, 'r', encoding='utf-8', errors='ignore') as f:
            answer_json = json.load(f)
        list_answers = {}
        for answer in answer_json:
            answer_key, answer_parsed = self._raw_answer_parsing(answer, cot=cot)
            list_answers.update({answer_key: {'answer': answer_parsed, 'raw_answer': answer.get('answer')}})
        self._list_answer = list_answers
        pipeline_logger.info(f'GlmJsonResult | load result data from {answer_file} end, '
                             f'total {len(self._list_answer)} answers.')


class ResultStrategy:
    def __init__(self, result_file_type: ResultDataFileType, question_type: QuestionType):
        self.__strategy = None
        self._get_strategy(result_file_type, question_type)

    def _get_strategy(self, result_file_type: ResultDataFileType, question_type: QuestionType):
        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if issubclass(cls, BaseResult) and cls.result_file_type() == result_file_type:
                self.__strategy = cls(question_type)
                break
        if self.__strategy is None:
            raise ValueError("please specify the question type in the `ResultDataFileType` enum class.")

    def load_result_data(self, answer_file, cot=False):
        self.__strategy.load_result_data(answer_file, cot)

    def list_answer(self):
        return self.__strategy.list_answer
