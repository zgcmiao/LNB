# -*- coding: utf-8 -*-
import logging.handlers

from .common_helper import CommonHelper
from conf import Conf

LOG_LEVEL_KEY = "LOG_LEVEL"
LOG_OUTPUT_PATH_KEY = "LOG_OUTPUT_PATH"
LOG_FORMAT_KEY = "LOG_FORMAT"


def get_logger(name):
    logger = logging.getLogger(name)
    # set log level
    logger.setLevel(Conf.LOG_SETTINGS.get("%s" % LOG_LEVEL_KEY))
    log_file_path = str(Conf.LOG_SETTINGS.get("%s" % LOG_OUTPUT_PATH_KEY)) % name
    is_exist, path = CommonHelper.judge_file_or_dir_exist(log_file_path)
    if not is_exist:
        CommonHelper.create_file(path)

    fileHandler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=300 * 1024 * 1024,
        backupCount=10
    )
    # output into file
    formatter = logging.Formatter(Conf.LOG_SETTINGS.get("%s" % LOG_FORMAT_KEY))
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    # output into stream
    shHeader = logging.StreamHandler()
    shHeader.setFormatter(formatter)
    logger.addHandler(shHeader)
    return logger


pipeline_logger = get_logger("pipeline_logger")
task_logger = get_logger("task_logger")
