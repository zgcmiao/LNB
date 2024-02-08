# -*- coding: utf-8 -*-
import os
from pathlib import Path
from time import sleep
from typing import Union
import uuid


class CommonHelper:
    @staticmethod
    def judge_file_or_dir_exist(path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)

        return (True, path) if path.exists() else (False, path)

    @staticmethod
    def create_file(path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).touch(exist_ok=True)

    @staticmethod
    def generate_uuid():
        return uuid.uuid1()

    @staticmethod
    def check_python_interpreter(python_interpreter_path):
        command = f"{python_interpreter_path} -c 'import os'"
        flag = os.system(command)
        return True if flag == 0 else False


if __name__ == '__main__':
    print(CommonHelper.generate_uuid())
    sleep(2)
    print(CommonHelper.generate_uuid())