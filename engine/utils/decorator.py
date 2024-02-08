# -*- coding: utf-8 -*-
import functools
import time
import traceback
from utils import pipeline_logger


def pipeline_logger_wrapper(func_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            logger_info = f"pipeline id: `{self.pipeline_id}` `model_name: {self.model_name}, model_type: {self.model_type}`"

            pipeline_logger.info(f"{logger_info}, {func_name} start.")
            start_time = time.time()
            try:
                value = func(self, *args, **kwargs)
            except Exception as ex:
                ex_str = traceback.format_exc()
                pipeline_logger.error(f"pipeline id: `{self.pipeline_id}` `model_name: {self.model_name}, model_type: {self.model_type}` "
                                      f"has an exception. exception: \n{ex_str}")
            end_time = time.time()
            dur_time = end_time - start_time
            pipeline_logger.info(f"{logger_info}, {func_name} finish, time: {str(round(dur_time, 2))}s", *args,
                                 **kwargs)
            return value

        return wrapper

    return decorator
