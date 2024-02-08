# -*- coding: utf-8 -*-
import abc
import inspect
import sys

from conf import QuestionType, LanguageType

UNDERLINED_SUFFIX = "____"


class QuestionPromptBase(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    @abc.abstractmethod
    def key(cls):
        pass

    @abc.abstractmethod
    def get_question_correct_answer(self, question: dict, *args, **kwargs):
        pass

    @abc.abstractmethod
    def generate_prompt_header(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def normalize_generating_prompts_inputs_func(self, question: dict, *args, **kwargs):
        pass

    @abc.abstractmethod
    def generate_prompt(self, *args, **kwargs):
        pass


class MultipleChoiceQuestionPromptStrategy(QuestionPromptBase):

    @classmethod
    def key(cls):
        return QuestionType.MULTIPLE_CHOICE

    def get_question_correct_answer(self, question: dict, *args, **kwargs):
        return question.get("answer", {}).get("choice", "")

    def generate_prompt_header(self, *args, **kwargs):
        subject_name = kwargs.get("subject_name")
        subject_zh_name = kwargs.get("subject_zh_name")
        target_language = kwargs.get("target_language") or LanguageType.EN

        if target_language == LanguageType.EN:
            prompt_header = f'The following are multiple choice questions (with answers) about {subject_name}.'
        else:
            prompt_header = f'以下是关于{subject_zh_name}的单项选择题（附答案）。'

        return prompt_header

    def normalize_generating_prompts_inputs_func(self, question: dict, *args, **kwargs):
        question_content = question.get("content", "")
        question_answer_choice = question.get("answer", {}).get("choice", "")
        question_answer_explanation = question.get("answer", {}).get("content", "")
        question_context = question.get("context", {})

        base_inputs = {
            "question_content": question_content,
            "question_answer_choice": question_answer_choice,
            "question_answer_explanation": question_answer_explanation,
            "question_context" : question_context,
            "question_choices": question.get("choices", []),
            **kwargs
        }
        return base_inputs

    def generate_prompt(self, *args, **kwargs):
        question_content = kwargs.get("question_content")
        question_choices = kwargs.get("question_choices")
        question_answer_choice = kwargs.get("question_answer_choice")
        question_answer_explanation = kwargs.get("question_answer_explanation")
        question_context = kwargs.get("question_context")
        target_language = kwargs.get("target_language") or LanguageType.EN
        cot = kwargs.get("cot", False)
        rag = kwargs.get("rag", False)
        with_answer = kwargs.get("with_answer", True)
        lines = []
        if rag:
            context = question_context
            lines.append("Use the following pieces of context to answer the question at the end.")
            lines.append(context[:1000])
        if target_language == LanguageType.EN:
            lines.append("Question:" + question_content)
        elif target_language == LanguageType.ZH:
            lines.append("问：" + question_content)
        for c in question_choices:
            lines.append(f"{c['name']}. {c['content']}")
        if with_answer:
            if cot:
                # assert explanation.find("Explanation:") < 0, "invalid cot example: no explanation found in " + question["title"]
                # getting index of substrings
                sub1 = "Explanation:"
                sub2 = "Reference"
                idx1 = question_answer_explanation.find(sub1)
                idx2 = question_answer_explanation.find(sub2)

                # length of substring 1 is added to
                # get string from next character
                res = question_answer_explanation[idx1: idx2]
                explanation = res
                lines.append("Let's think step by step.")
                lines.append(explanation)
                lines.append('Answer: ' + question_answer_choice)
            else:
                if target_language == LanguageType.EN:
                    lines.append('Answer: ' + question_answer_choice)
                elif target_language == LanguageType.ZH:
                    lines.append('答：' + question_answer_choice)
        else:
            if cot:
                # lines.append("Explanation:")
                lines.append("Answer:Let's think step by step.")
            else:
                if target_language == LanguageType.EN:
                    lines.append('Answer:')
                elif target_language == LanguageType.ZH:
                    lines.append('')
        return '\n'.join(lines)


class CLOZEQuestionPromptStrategy(QuestionPromptBase):

    @classmethod
    def key(cls):
        return QuestionType.CLOZE

    def get_question_correct_answer(self, question: dict, *args, **kwargs):
        return question.get("answer", "")

    def generate_prompt_header(self, *args, **kwargs):
        subject_name = kwargs.get("subject_name")
        subject_zh_name = kwargs.get("subject_zh_name")
        target_language = kwargs.get("target_language") or LanguageType.EN

        if target_language == LanguageType.EN:
            prompt_header = f'The following are questions (with answers) about {subject_name}. Please fill in the answer in the underlined position.'
        else:
            prompt_header = f'以下是关于{subject_zh_name}的填空题，请将答案填写在下划线的位置。'

        return prompt_header

    def normalize_generating_prompts_inputs_func(self, question: dict, *args, **kwargs):
        question_content = question.get("content", "")
        question_answer = question.get("answer", "")

        base_inputs = {
            "question_content": question_content,
            "question_answer": question_answer,
            **kwargs
        }
        return base_inputs

    def generate_prompt(self, *args, **kwargs):
        question_content = kwargs.get("question_content")
        question_answer = kwargs.get("question_answer")
        target_language = kwargs.get("target_language") or LanguageType.EN
        cot = kwargs.get("cot", False)
        rag = kwargs.get("rag", False)
        with_answer = kwargs.get("with_answer", True)

        if target_language == LanguageType.EN:
            lines = ["Question:" + question_content]
        elif target_language == LanguageType.ZH:
            lines = ["问：" + question_content]
        if with_answer:
            if cot:
                pass
                # assert explanation.find("Explanation:") < 0, "invalid cot example: no explanation found in " + question["title"]
                # getting index of substrings
                # sub1 = "Explanation:"
                # sub2 = "Reference"
                # idx1 = question_answer_explanation.find(sub1)
                # idx2 = question_answer_explanation.find(sub2)

                # length of substring 1 is added to
                # get string from next character
                # res = question_answer_explanation[idx1: idx2]
                # explanation = res
                # lines.append("Let's think step by step.")
                # lines.append(explanation)
                # lines.append('Answer: ' + question_answer_choice)
            else:
                if target_language == LanguageType.EN:
                    lines.append('Answer: ' + question_answer)
                elif target_language == LanguageType.ZH:
                    lines.append('答：' + question_answer)
        else:
            if cot:
                # lines.append("Explanation:")
                lines.append("Answer:Let's think step by step.")
            else:
                if target_language == LanguageType.EN:
                    lines.append('Answer:')
                elif target_language == LanguageType.ZH:
                    lines.append('')
        return '\n'.join(lines)


class QAQuestionPromptStrategy(QuestionPromptBase):

    @classmethod
    def key(cls):
        return QuestionType.QUESTION_AND_ANSWER

    def get_question_correct_answer(self, question: dict, *args, **kwargs):
        return question.get("answer", "")

    def generate_prompt_header(self, *args, **kwargs):
        subject_name = kwargs.get("subject_name")
        subject_zh_name = kwargs.get("subject_zh_name")
        target_language = kwargs.get("target_language") or LanguageType.EN

        if target_language == LanguageType.EN:
            prompt_header = f'The following are questions about {subject_name}.'
        else:
            prompt_header = f'以下是关于{subject_zh_name}的问答题.'

        return prompt_header

    def normalize_generating_prompts_inputs_func(self, question: dict, *args, **kwargs):
        question_content = question.get("content", "")
        question_answer = question.get("answer", "")

        base_inputs = {
            "question_content": question_content,
            "question_answer": question_answer,
            **kwargs
        }
        return base_inputs

    def generate_prompt(self, *args, **kwargs):
        question_content = kwargs.get("question_content")
        question_answer = kwargs.get("question_answer")
        target_language = kwargs.get("target_language") or LanguageType.EN
        cot = kwargs.get("cot", False)
        with_answer = kwargs.get("with_answer", True)

        if target_language == LanguageType.EN:
            lines = ["Question:" + question_content]
            # lines = [question_content]
        elif target_language == LanguageType.ZH:
            lines = ["问：" + question_content]
        if with_answer:
            if cot:
                pass
                # assert explanation.find("Explanation:") < 0, "invalid cot example: no explanation found in " + question["title"]
                # getting index of substrings
                # sub1 = "Explanation:"
                # sub2 = "Reference"
                # idx1 = question_answer_explanation.find(sub1)
                # idx2 = question_answer_explanation.find(sub2)

                # length of substring 1 is added to
                # get string from next character
                # res = question_answer_explanation[idx1: idx2]
                # explanation = res
                # lines.append("Let's think step by step.")
                # lines.append(explanation)
                # lines.append('Answer: ' + question_answer_choice)
            else:
                if target_language == LanguageType.EN:
                    lines.append('Answer: ' + question_answer)
                elif target_language == LanguageType.ZH:
                    lines.append('答：' + question_answer)
        else:
            if cot:
                # lines.append("Explanation:")
                lines.append("Answer:Let's think step by step.")
            else:
                if target_language == LanguageType.EN:
                    lines.append('Answer:')
                elif target_language == LanguageType.ZH:
                    lines.append('')
        return '\n'.join(lines)

class QuestionPromptStrategy:
    """ Question Prompt Strategy

    Get strategies based on different question types
    """

    def __init__(self, question_type: QuestionType):
        self._get_strategy(question_type)

    def _get_strategy(self, question_type: QuestionType) -> QuestionPromptBase:
        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if issubclass(cls, QuestionPromptBase) and cls.key() == question_type:
                self.__strategy = cls()
                return
        if self.__strategy is None:
            raise ValueError("please specify the question type in the `QuestionType` enum class.")

    def get_question_correct_answer(self, question: dict, *args, **kwargs):
        return self.__strategy.get_question_correct_answer(question, *args, **kwargs)

    def generate_prompt_header(self, *args, **kwargs):
        return self.__strategy.generate_prompt_header(*args, **kwargs)

    def normalize_generating_prompts_inputs_func(self, question: dict, *args, **kwargs):
        return self.__strategy.normalize_generating_prompts_inputs_func(question, *args, **kwargs)

    def generate_prompt(self, *args, **kwargs):
        return self.__strategy.generate_prompt(*args, **kwargs)


def question_format_convert_handler(raw_question_type: QuestionType,
                                    target_question_type: QuestionType,
                                    raw_question: dict, **kwargs):
    if raw_question_type == QuestionType.MULTIPLE_CHOICE and target_question_type == QuestionType.CLOZE:
        choice_map = {c['name'].replace('.', ''): c['content'] for c in raw_question['choices']}
        return {
            "question_content": f'{raw_question.get("content", "")} {UNDERLINED_SUFFIX}',
            "question_answer": choice_map.get(raw_question.get("answer", {}).get("choice", "")),
            **kwargs
        }
    elif raw_question_type == QuestionType.MULTIPLE_CHOICE and target_question_type == QuestionType.QUESTION_AND_ANSWER:
        choice_map = {c['name'].replace('.', ''): c['content'] for c in raw_question['choices']}
        return {
            "question_content": f'{raw_question.get("content", "")} {UNDERLINED_SUFFIX}',
            "question_answer": choice_map.get(raw_question.get("answer", {}).get("choice", "")),
            **kwargs
        }
    return None

