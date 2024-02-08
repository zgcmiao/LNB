# -*- coding: utf-8 -*-
import torch

from model import ModelType


# TODO: convert get model inference params from configure yaml
def get_params_by_model_type(model_type, model_name):
    model_params = {}
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

    if model_type == ModelType.LLAMA2:
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

    elif model_type == ModelType.FALCON:
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

    elif model_type == ModelType.BAICHUAN:
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
                "use_fast": False,
                "add_bos_token": False,
                "model_max_length": 4096,
                "padding_side": "left",
                "trust_remote_code": True
            },
            "auto_model_causalml_params":
                {
                    "torch_dtype": torch.bfloat16,
                    "top_p": 0.8,
                    "temperature": 0.8,
                    "trust_remote_code": True
                },
            "model_inference_params":
                {
                },
            "first_gen_explanation_for_inference": True
        }
    elif model_type == ModelType.CHATGLM2:
        model_params = {
            "model_tokenizer_params": {
                "use_fast": False,
                "add_bos_token": False,
                "model_max_length": 4096,
                "padding_side": "left",
                "trust_remote_code": True
            },
            "auto_model_causalml_params":
                {
                    "torch_dtype": torch.bfloat16,
                    "top_p": 0.8,
                    "temperature": 0.8,
                    "trust_remote_code": True
                },
            "model_inference_params":
                {
                },
            "first_gen_explanation_for_inference": True
        }

    elif model_type == ModelType.MIXTRAL:
        model_params = {
            "model_tokenizer_params": {
                "trust_remote_code": True
            },
            "auto_model_causalml_params":
                {
                    "device_map": "auto" if torch.cuda.is_available() else None,
                    "trust_remote_code": True
                },
        }
    return model_params
