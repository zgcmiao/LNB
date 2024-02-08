# Inference Engine

The inference engine is the core component for driving the model inference on various benchmark tasks, including both
the [written exam tasks](#written-exam-tasks) and the [lab exam tasks](#lab-exam-tasks).

## Prerequisites

### Python environment

This engine requires Python (version >= `3.10`). Use the following command to install the dependencies.

```bash
pip install -r requirements.txt
```

**Note**: For benchmarking Mixtral models, please use `pip install -r requirements-mixtral.txt` instead.

### NFS Shared Folder (Optional)

To share the question bank with all the systems, you need to create a shared folder in NFS (Network File System).
Please refer to [Ubuntu Server Docs](https://ubuntu.com/server/docs/service-nfs) for installation instructions.

You may mount the shared folder to a canonical mount point, denoted as `<NFS_PATH>`, in all the nodes in the cluster,
and then use the following commands to copy the question bank to the shared folder.

```bash
export NFS_PATH=<NFS_PATH>
cp -rp engine/data/question_bank "${NFS_PATH}" 
```

**Note:** This shared folder is not required if you only want to run the inference engine manually.

### Lab Environment Dependencies (Optional)

Should you want to run the lab exams, please install the system dependencies as follows.

```bash
sudo apt install mininet frr openvswitch-testcontroller
```

**Note:**

1. We use `Ubuntu 22.04` as the OS. If you want to run lab exams in a different OS, please find the required
   system dependencies by yourself.
2. The tested versions of these packages that are compatible with our code
   are: `mininet=2.3.0`, `frr=8.1`, `openvswitch-testcontroller=2.17.8`.

### OpenAI API Key (Optional)

Should you want to benchmark OpenAI models, please obtain an API key first.

## Run Inference

```bash
python run_models.py --list_model <model_list> ...
```

Details of the parameters are listed below.

## Supported Models

| Family            | Models                                                                                                                                                                                    |  
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LLaMA             | `huggyllama/llama-7b`, `huggyllama/llama-13b`, `huggyllama/llama-30b`, `huggyllama/llama-65b`                                                                                             |   
| LLaMA 2           | `meta-llama/Llama-2-7b-hf`, `meta-llama/Llama-2-7b-chat-hf`, `meta-llama/Llama-2-13b-hf`, `meta-llama/Llama-2-13b-chat-hf`, `meta-llama/Llama-2-70b-hf`, `meta-llama/Llama-2-70b-chat-hf` | 
| Falcon            | `tiiuae/falcon-7b`, `tiiuae/falcon-7b-instruct`, `tiiuae/falcon-40b`, `tiiuae/falcon-40b-instruct`, `THUDM/chatglm-6b`, `THUDM/chatglm2-6b`                                               | 
| Baichuan          | `baichuan-inc/baichuan-7B`, `baichuan-inc/Baichuan-13B-Base`, `baichuan-inc/Baichuan-13B-Chat`                                                                                            | 
| Mixtral           | `mistralai/Mixtral-8x7B-v0.1`, `mistralai/Mixtral-8x7B-Instruct-v0.1`                                                                                                                     |
| OpenAI            | `gpt-3.5-turbo`, `gpt-4`                                                                                                                                                                  |
| Customized Models | `customized-model`                                                                                                                                                                        |

You may specify a list of supported models to run with `--list_model`,
*e.g.* `--list_model huggyllama/llama-7b huggyllama/llama-13b`.

### Notes for OpenAI Models

When you put OpenAI models in the model list, you also need to specify all the additional parameters as follows.

1. `--api_key` to provide the OpenAI API key, *e.g.* `--api_key sk-ABCDEFG123-puNk`.
2. `--data_path` is the path to the prompt dump, which should be generated
   by [script/preprosess_data/generate_prompt.py](script/preprosess_data/generate_prompt.py). This is required due to
   our legacy code structure for OpenAI models. For your convenience, we have included some generated dump files in the
   question bank, *e.g.* `--data_path data/question_bank/written_exam/mcq_gpt_zero_shot.json`.

### Notes for Customized Models

When you put `customized-model` in the model list, you also need to specify `--customized_model_package` to provide the
path to the Python module file of the customized LLM.

The customized LLM must be a subclass of `langchain_core.language_models.llms.LLM`. Please refer to the
[LangChain Documentation](https://api.python.langchain.com/en/latest/language_models/langchain_core.language_models.llms.LLM.html)
for more details.

## Supported Tasks

### Written Exam Tasks

**1. Multiple Choice Question (MCQ)**

```bash
# Zero-Shot Prompt, RegEx-Based Extraction 
python run_models.py --list_model <model_list> --list_subject mcq --list_shot_type zero-shot

# Five-Shot Prompt, RegEx-Based Extraction
python run_models.py --list_model <model_list> --list_subject mcq --list_shot_type five-shot

# Zero-Shot Prompt, Logits-Based Extraction
python run_models.py --list_model <model_list> --list_subject mcq --list_shot_type zero-shot --version logits

# Five-Shot Prompt, Logits-Based Extraction
python run_models.py --list_model <model_list> --list_subject mcq --list_shot_type five-shot --version logits

# RAG Prompt (Zero-Shot), Logits-Based Extraction
python run_models.py --list_model <model_list> --list_subject mcq_rag --list_shot_type zero-shot --version logits --rag

# Five-Shot-CoT Prompt, Logits-Based Extraction
python run_models.py --list_model <model_list> --list_subject mcq_cot --list_shot_type five-shot --pre_gen_explanation_for_inference --version logits --cot
```

**2. Configuration Translation Questions (CTQ)**

```bash
python run_models.py  --list_model <model_list> --question_type configuration_translation
```

### Lab Exam Tasks

**1. Intent Completion**

```bash
# Topology Comprehension
python run_models.py --list_model <model_list> --question_type lab_exam --list_subject intent_completion_topo_comprehension 

# Command Execution
python run_models.py --list_model <model_list> --question_type lab_exam --list_subject intent_completion_command_execution
```

**2. Operational Safety**

```bash
python run_models.py --list_model <model_list> --question_type lab_exam --list_subject operational_safety 
```

## Resuming Interrupted Task

This engine supports resuming a previous task that was interrupted due to any reason, *e.g.* unavailable resource,
internal error or external interference, by specifying the output path and pipeline ID of the interrupted task.

```bash
# Resume interrupted task at given path (Zero-Shot MCQ as an example)
python run_models.py --list_model <model_list> --list_subject mcq --list_shot_type zero-shot --breakpoint_file <output_path> --breakpoint_pipeline_id <pipeline_id>
```

## Reference

See [reference.md](reference.md) for more details.
