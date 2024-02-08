# Inference Engine for Distributed Benchmark System

The Inference Engine is a core component of the Distributed Benchmark System. Its primary function is to load large
language models and perform evaluation tasks using strategies like shot, rag, cot, etc.

The project includes:

1. A set of question banks is provided, including written tests, laboratory tests, and configuration translation tasks.
2. Command-line tools for running LLMs evaluate tasks, supporting shot, cot, rag, and other strategies.
3. Provides an interface for customized LLM that can evaluate specified data set tasks on customized LLM.

## Core Components

| `Components`             | `Description`                                                                                         |
|--------------------------|-------------------------------------------------------------------------------------------------------|
| conf                     | Project configuration                                                                                 |
| data                     | Question_bank containing Writing-Exam/Lab-Exam/configuration_translation                              |
| evaluation_pipeline      | Evaluation tasks are operated through specified pipelines                                             |
| model                    | Houses all models                                                                                     |
| script                   | Contains executable files, prompt generation scripts, result post-processing and other helper scripts |
| utils                    | Collection of common components                                                                       |
| run_models.py            | Project entry file                                                                                    |
| requirements.txt         | Dependent packages                                                                                    |
| requirements-mixtral.txt | Mixtral model’s special dependency packages                                                           |
| Dockerfile               | Dockerfile                                                                                            |
| Dockerfile-mixtral       | Mixtral model’s Dockerfile                                                                            |
| README.md                | Introduction to the project and documentation entrance                                                |

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Pre-execution Check](#pre-execution check)
  - [Writen Exam](#writen exam)
  - [Lab Exam](#lab exam)
- [Script Tool](#script tool)
  - [Customized LLM](#customized llm)

## Installation

Use the following steps to install the Inference Engine:

```sh
# TODO: specify llm-bench name replace `<llm-bench-name>`

# Clone the repository
$ git clone --recursive https://github.com/example/<llm-bench-name>.git

# Set the environment variable PYTHONPATH to the current working directory. 
$ export PYTHONPATH=${PWD}

# Change to the project directory
cd <llm-bench-name>
```

## Usage

### Pre-execution Check

In this project, the model evaluation task will load the configuration file in the program to load the model
configuration parameters and execute the task.

**Note：*Please check the parameters in the `model_configuration_params.py` file before executing the task*:**

```sh
# Check the configuration file parameter. version contains regex and logits.
$ view <project_root_path>/evaluation_pipeline/<version>/model_configuration_params.py.
```

For example, if you want to execute a `LLAMA` model, you can find the corresponding `LLAMA` configuration block in the
`model_configuration_params.py` configuration file and modify the parameters in it.

``` python
...
    
if model_type == ModelType.LLAMA:
    model_params = {
        "model_tokenizer_params": {
            "use_fast": False,
            "add_bos_token": False,
            "model_max_length": 4096,
            "padding_side": "right",
            "trust_remote_code": True
        },
        "auto_model_causalml_params":
            {
                "device_map": "auto" if torch.cuda.is_available() else None,
                "trust_remote_code": True
            },
        "model_inference_params":
            {
                "max_new_tokens": 20,
            },
        "first_gen_explanation_for_inference": True
    }
    
...
```

Run the program through the following command line. It supports two types of questions: `Written Exam` and `Lab Exam`.

### Writen Exam

#### Command Line

```sh
$ python3 run_models.py  
  --list_model <list_model> 
  --list_subject <list_subject> 
  --list_shot_type <list_shot_type>
  --question_type <question_type>
  --metric_name <metric_name>
  --language_type <language_type> 
  --breakpoint_pipeline_id <breakpoint_pipeline_id> 
  --breakpoint_file <breakpoint_file> 
  --list_finetune_weights <list_finetune_weights>
  --dry-run | --no-dry-run
  --cot | --no-cot 
  --rag | --no-rag
  --need_merge_weights | --no-need_merge_weights
  --pre_gen_explanation_for_inference | --no-pre_gen_explanation_for_inference
```

#### Parameter Description

| Name                              | Description                                                                                       | Required | Value Range             | Default               |
|-----------------------------------|---------------------------------------------------------------------------------------------------|----------|-------------------------|-----------------------|
| list_model                        | Evaluation model list                                                                             | Y        | Table description below |                       |
| list_subject                      | Subject name of evaluation questions                                                              | N        | Table description below | security              |
| list_shot_type                    | Evaluation shot type                                                                              | N        | Table description below | zero-shot & five-shot |
| question_type                     | Evaluation question type                                                                          | N        | Table description below | multiple_choice       |
| metric_name                       | Evaluation metric name                                                                            | N        | Table description below | exact                 |
| language_type                     | Evaluation prompt language type                                                                   | N        | Table description below | EN                    |
| breakpoint_pipeline_id            | Supports incremental execution of evaluation tasks, `pipelineId` of the last evaluation execution | N        |                         |                       |
| breakpoint_file                   | Supports incremental execution of evaluation tasks, `file path` of the last evaluation execution  | N        |                         |                       |
| list_finetune_weights             | Fine-tuning the weight path                                                                       | N        |                         |                       |
| version                           | Version for calculate accuracy based                                                              | N        | Table description below | regex                 |
| dry-run                           | The test program executes, but does not actually execute                                          | N        |                         | False                 |
| cot                               | Chain-of-Thought Strategy                                                                         | N        |                         | False                 |
| rag                               | Retrieval Augmented Generation Strategy                                                           | N        |                         | False                 |
| need_merge_weights                | Fine-tuning weights need to be merged                                                             | N        |                         | False                 |
| pre_gen_explanation_for_inference |                                                                                                   | N        |                         | False                 |

| `list_model`                   | 
|--------------------------------| 
| huggyllama/llama-7b            | 
| huggyllama/llama-13b           | 
| huggyllama/llama-30b           | 
| huggyllama/llama-65b           | 
| meta-llama/Llama-2-7b-hf       | 
| meta-llama/Llama-2-7b-chat-hf  | 
| meta-llama/Llama-2-13b-hf      | 
| meta-llama/Llama-2-13b-chat-hf | 
| meta-llama/Llama-2-70b-hf      | 
| meta-llama/Llama-2-70b-chat-hf | 
| tiiuae/falcon-7b               | 
| tiiuae/falcon-7b-instruct      | 
| tiiuae/falcon-40b              | 
| tiiuae/falcon-40b-instruct     |  
| THUDM/chatglm-6b               | 
| THUDM/chatglm2-6b              | 
| baichuan-inc/baichuan-7B       | 
| baichuan-inc/Baichuan-13B-Base | 
| baichuan-inc/Baichuan-13B-Chat |

| `list_subject` | `Description`                                                      |
|----------------|--------------------------------------------------------------------|
| mcq            | multiple-choice questions                                          |
| mcq-rag        | multiple-choice questions with Retrieval-Augmented-Generation info |
| mcq-cot        | multiple-choice questions with Few-Shot Chain-of-Thought info      |

| `list_shot_type` | 
|------------------| 
| zero-shot        | 
| five-shot        |

| `question_type` | 
|-----------------| 
| multiple_choice | 
| cloze           |
| qa              |

| `metric_name` | 
|---------------| 
| exact         | 
| bleu          |
| rouge         |

| `language_type` |
|-----------------|
| en              |
| zh              |

| `version` |
|-----------| 
| regex     | 
| logits    |

#### Examples

```sh
# zero-shot & calculate accuracy RegEx-based 
$ python3 run_models.py --list_model huggyllama/llama-7b --list_subject mcq --list_shot_type zero-shot

# five-shot & calculate accuracy RegEx-based
$ python3 run_models.py --list_model huggyllama/llama-7b --list_subject mcq --list_shot_type five-shot

# zero-shot & calculate accuracy logits-based
$ python3 run_models.py --list_model huggyllama/llama-7b --list_subject mcq --list_shot_type zero-shot --version logits

# five-shot & calculate accuracy logits-based
$ python3 run_models.py --list_model huggyllama/llama-7b --list_subject mcq --list_shot_type five-shot --version logits

# zero-shot & rag & calculate accuracy logits-based
$ python3 run_models.py --list_model huggyllama/llama-7b --list_subject mcq_rag --list_shot_type zero-shot --version logits --rag

# five-shot & rag & calculate accuracy logits-based
$ python3 run_models.py --list_model huggyllama/llama-7b --list_subject mcq_cot --list_shot_type five-shot --pre_gen_explanation_for_inference --version logits --cot

# continue task execution at breakpoint
$ python3 run_models.py --list_model huggyllama/llama-7b --list_subject mcq --list_shot_type zero-shot --no-dry-run --breakpoint_file output/model/huggyllama-llama-7b/8f9e762d-6c8e-11ee-8b2b-0c9a3c8ebd26.auto.security-zero-shot.json --breakpoint_pipeline_id 8f9e762d-6c8e-11ee-8b2b-0c9a3c8ebd26
```

### Lab Exam

#### Command Line

```sh
$ python3 run_models.py 
--list_subject intent_completion_command_execution intent_completion_topo_comprehension operational_safety 
--list_model huggyllama/llama-7b 
--question_type lab_exam
--version regex
```

#### Parameter Description

| Name          | Description                          | Required | Value Range             | Default         |
|---------------|--------------------------------------|----------|-------------------------|-----------------|
| list_model    | Evaluation model list                | Y        | Table description below |                 |
| list_subject  | Subject name of evaluation questions | Y        | Table description below | security        |
| question_type | Evaluation question type             | Y        | lab_exam                | multiple_choice |
| version       | Version for calculate accuracy based | N        | regex                   | regex           |

| `list_model`                   | 
|--------------------------------| 
| huggyllama/llama-7b            | 
| huggyllama/llama-13b           | 
| huggyllama/llama-30b           | 
| huggyllama/llama-65b           | 
| meta-llama/Llama-2-7b-hf       | 
| meta-llama/Llama-2-7b-chat-hf  | 
| meta-llama/Llama-2-13b-hf      | 
| meta-llama/Llama-2-13b-chat-hf | 
| meta-llama/Llama-2-70b-hf      | 
| meta-llama/Llama-2-70b-chat-hf | 
| tiiuae/falcon-7b               | 
| tiiuae/falcon-7b-instruct      | 
| tiiuae/falcon-40b              | 
| tiiuae/falcon-40b-instruct     |  
| THUDM/chatglm-6b               | 
| THUDM/chatglm2-6b              | 
| baichuan-inc/baichuan-7B       | 
| baichuan-inc/Baichuan-13B-Base | 
| baichuan-inc/Baichuan-13B-Chat |

| `list_subject`                       | `Description`                                                                  |
|--------------------------------------|--------------------------------------------------------------------------------|
| intent_completion_command_execution  | QA with command execution phase of intent completion tasks                     |
| intent_completion_topo_comprehension | QA with JSON-formatted topology comprehension phase of intent completion tasks |
| operational_safety                   | QA with malicious NetOps intents                                               |

#### Examples

```sh
$ python3 run_models.py --list_subject completion json_topo operation_safety --list_model huggyllama/llama-7b --question_type lab_exam
```

### Network Configuration Translation

#### Command Line

```sh
$ python3 run_models.py  
  --list_model <list_model> 
  --question_type configuration_translation
  --version regex
```

#### Parameter Description

| Name          | Description                          | Required | Value Range               | Default         |
|---------------|--------------------------------------|----------|---------------------------|-----------------|
| list_model    | Evaluation model list                | Y        | Table description below   |                 |
| question_type | Evaluation question type             | Y        | configuration_translation | multiple_choice |
| version       | Version for calculate accuracy based | N        | regex                     | regex           |

| `list_model`                   | 
|--------------------------------| 
| huggyllama/llama-7b            | 
| huggyllama/llama-13b           | 
| huggyllama/llama-30b           | 
| huggyllama/llama-65b           | 
| meta-llama/Llama-2-7b-hf       | 
| meta-llama/Llama-2-7b-chat-hf  | 
| meta-llama/Llama-2-13b-hf      | 
| meta-llama/Llama-2-13b-chat-hf | 
| meta-llama/Llama-2-70b-hf      | 
| meta-llama/Llama-2-70b-chat-hf | 
| tiiuae/falcon-7b               | 
| tiiuae/falcon-7b-instruct      | 
| tiiuae/falcon-40b              | 
| tiiuae/falcon-40b-instruct     |  
| THUDM/chatglm-6b               | 
| THUDM/chatglm2-6b              | 
| baichuan-inc/baichuan-7B       | 
| baichuan-inc/Baichuan-13B-Base | 
| baichuan-inc/Baichuan-13B-Chat |

#### Examples

```sh
$ python run_models.py --list_model huggyllama/llama-7b --question_type configuration_translation --version regex
```
