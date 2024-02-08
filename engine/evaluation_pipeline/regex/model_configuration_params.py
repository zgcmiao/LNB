# -*- coding: utf-8 -*-
import torch

from model import ModelType


# TODO: convert get model inference params from configure yaml
def get_params_by_model_type(model_type, model_name):
    model_params = {}
    if model_type == ModelType.LLAMA:
        model_params = {
            "model_pipeline_params":
                {
                    "device": None if torch.cuda.is_available() else -1,
                    "device_map": "auto" if torch.cuda.is_available() else None,
                    "task": "text-generation",
                    "cache_prompt_prefix": True
                },
            "model_inference_params":
                {
                    "max_new_tokens": 20,
                    "batch_size": 4
                },
            # "enable_local_transformers": True
        }

    if model_type == ModelType.LLAMA2:
        model_params = {
            "model_pipeline_params":
                {
                    "device": None if torch.cuda.is_available() else -1,
                    "device_map": "auto" if torch.cuda.is_available() else None,
                    "task": "text-generation",
                    "cache_prompt_prefix": True
                },
            "model_inference_params":
                {
                    "max_new_tokens": 20,
                    "batch_size": 4
                },
            # "enable_local_transformers": True
        }

    elif model_type == ModelType.FALCON:
        model_params = {
            "model_pipeline_params":
                {
                    "device": None if torch.cuda.is_available() else -1,
                    "device_map": "auto" if torch.cuda.is_available() else None,
                    "torch_dtype": torch.bfloat16,
                    "trust_remote_code": True,
                    "task": "text-generation"
                },
            "model_inference_params":
                {
                    "max_new_tokens": 20,
                    "num_return_sequences": 1
                },
            "enable_local_transformers": True
        }

    elif model_type == ModelType.BAICHUAN:
        # model_pipeline_params does not allow the `device` field
        model_params = {
            "model_tokenizer_params": {
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
                    "repetition_penalty": 1.1
                },
            "model_pipeline_params": {
                "device": None if torch.cuda.is_available() else -1,
                "device_map": "auto" if torch.cuda.is_available() else None,
                "task": "text-generation",
                "trust_remote_code": True,
            }
        }

    elif model_type == ModelType.GLM:
        model_params = {
            "model_tokenizer_params": {
                "trust_remote_code": True
            },
            "auto_model_causalml_params":
                {
                    "trust_remote_code": True
                },
            "model_inference_params":
                {
                    "max_length": 512
                }
        }

    elif model_type == ModelType.CHATGLM:
        model_params = {
            "model_tokenizer_params": {
                "trust_remote_code": True
            },
            "auto_model_params":
                {
                    "trust_remote_code": True
                },
            "model_inference_params":
                {
                }
        }
    elif model_type == ModelType.MIXTRAL:
        model_params = {
            "model_pipeline_params":
                {
                    "device": None if torch.cuda.is_available() else -1,
                    "device_map": "auto" if torch.cuda.is_available() else None,
                    "task": "text-generation",
                    "cache_prompt_prefix": True
                },
            "model_inference_params":
                {
                    "max_new_tokens": 20,
                    "batch_size": 4
                },
        }
    return model_params
