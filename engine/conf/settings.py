# -*- coding: utf-8 -*-

import logging
from pathlib import Path


class Conf:
    BASE_PATH = Path(__file__).parent.parent

    DEFAULT_VERSION = "regex"

    # log settings
    LOG_SETTINGS = {
        "LOG_NAME": "DEV",
        "LOG_LEVEL": logging.INFO,
        "LOG_OUTPUT_PATH": BASE_PATH / "output/log/%s.log",
        "LOG_FORMAT": "%(asctime)s %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
    }

    PYTHON_INTERPRETER_PATH = "python3"

    ENV_TRANSFORMERS_OFFLINE = 'TRANSFORMERS_OFFLINE'

    ENV_HF_EVALUATE_OFFLINE = 'HF_EVALUATE_OFFLINE'

    ENV_LIST = {
        f"{ENV_TRANSFORMERS_OFFLINE}": "1",
        f"{ENV_HF_EVALUATE_OFFLINE}": "1"
    }
