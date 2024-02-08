from src.dms.utils.common_utils import BaseEnum


class TaskTypeEnum(BaseEnum):
    Inference = 'Inference'  # inference task


class TaskStatusEnum(BaseEnum):
    CREATED = 'CREATED'      # task created
    PENDING = 'PENDING'      # task pending to run
    RUNNING = 'RUNNING'      # task running
    SUCCESS = 'SUCCESS'      # task success
    FAILED = 'FAILED'        # task failed
    DONE = 'DONE'            # task done, already save output result

    EXECUTED = 'EXECUTED'    # task executed
    INTERRUPT = 'INTERRUPT'  # task interrupt
    OPERATION = 'OPERATION'  # task exception

    DELETED = 'DELETED'      # task deleted


class QuestionType(BaseEnum):
    MULTIPLE_CHOICE = "multiple_choice"
    CLOZE = "cloze"
    QUESTION_AND_ANSWER = "qa"
