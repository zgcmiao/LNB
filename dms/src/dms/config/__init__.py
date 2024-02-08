# -*- coding: utf-8 -*-

from pathlib import Path

BASE_PATH = Path(__file__).parent.parent

CONFIG_MAPPER = {
    "dev": BASE_PATH / "config/dev_config.py",
    "prod": BASE_PATH / "config/prod_config.py"
}
