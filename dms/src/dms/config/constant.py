# task_config params
import os

TASK_SPLIT_BATCHES = 'split_batches'
TASK_LIST_SUBJECT = 'list_subject'
TASK_LIST_SHOT_TYPE = 'list_shot_type'
TASK_LIST_MODEL = 'list_model'
TASK_SUBJECT_ABSOLUTE_DIR = 'subject_absolute_dir'
TASK_DATA_ABSOLUTE_ROOT = 'data_absolute_root'
TASK_SUBJECT_ABSOLUTE_FILE_PATH = 'subject_absolute_file_path'
TASK_DATA_ABSOLUTE_FILE_PATH = 'data_absolute_file_path'
TASK_BREAKPOINT_FILE_PARAM = 'breakpoint_file'
TASK_QUESTION_TYPE = 'question_type'
TASK_LLM_BENCH_DOCKER_VERSION = 'llm_bench_docker_version'
TASK_LLM_BENCH_VERSION = 'llm_bench_version'
TASK_COT_PARAM = 'cot'
TASK_RAG_PARAM = 'rag'
TASK_PREFER_SUBJECT_PREFIX = 'prefer_subject_prefix'

DEFAULT_SHOT_TYPES = ['zero-shot', 'five-shot']

# sub_task
SUB_TASK_FILE_NAME_FORMAT = '{task_id}-{index}'
SUB_TASK_SUBJECT_FILE_NAME_FORMAT = '{subject}-{task_id}-{index}'
SUB_TASK_SUBJECT_NAME = 'Computer Network'
SUB_TASK_ID_FORMAT = '{subject}-{task_id}-{index}'
COMMAND_FORMAT = 'docker run --rm -v ~/.cache/huggingface/hub/{model_path}:/root/.cache/huggingface/hub/{model_path} ' \
                 '-v {nfs_path}/{{sub_task_id}}/output:/llm-bench/output --gpus all --name {{sub_task_id}} ' \
                 '-e PYTHONPATH=/llm-bench llm-bench:{llm_bench_docker_version} ' \
                 'python3 run_models.py --list_model {model_name} --list_subject {list_subject}' \
                 ' --list_shot_type {list_shot_type} --version {llm_bench_version} --no-dry_run'
DOCKER_NAME_FORMAT = 'llmbench-{task_id}-{index}'
DATA_SOURCE_DIR = 'source'
SUBJECT_DIR = 'subjects'
RESULT_FILE_PATH = '{nfs_path}/llm-bench-result/{task_id}'

DEFAULT_LLM_BENCH_DOCKER_VERSION = 'latest'
DEFAULT_LLM_BENCH_VERSION = 'regex'


# subject params
SUBJECT_EXAM_FILE = 'exam_files'
SUBJECT_NAME = 'name'

DEFAULT_SUBJECT_DATA = {
  "name": "Computer Network",
  "examples": [
    {
      "exam_id": "shot-examples",
      "question_id": "Question 1"
    },
    {
      "exam_id": "shot-examples",
      "question_id": "Question 2"
    },
    {
      "exam_id": "shot-examples",
      "question_id": "Question 3"
    },
    {
      "exam_id": "shot-examples",
      "question_id": "Question 4"
    },
    {
      "exam_id": "shot-examples",
      "question_id": "Question 5"
    }
  ],
  "exam_files": [

  ],
  "example_files": [
    "metadata/shot-examples.json"
  ]
}

DEFAULT_COT_SUBJECT_DATA = {
  "name": "Computer Network",
  "examples": [
    {
      "exam_id": "cot-shot-examples",
      "question_id": "Question 1"
    },
    {
      "exam_id": "cot-shot-examples",
      "question_id": "Question 2"
    },
    {
      "exam_id": "cot-shot-examples",
      "question_id": "Question 3"
    },
    {
      "exam_id": "cot-shot-examples",
      "question_id": "Question 4"
    },
    {
      "exam_id": "cot-shot-examples",
      "question_id": "Question 5"
    }
  ],
  "exam_files": [
  ],
  "example_files": [
    "metadata/cot-shot-examples.json"
  ]
}
