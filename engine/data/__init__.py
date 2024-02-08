# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Union
from conf import Conf, ParameterError
from utils import BaseManager

module_path = 'data'


class DataManager(BaseManager):
    """ Data manager

    Manage data, provide version control of data, etc.
    """

    def __init__(self, *args, **kwargs):
        """ Init manager

        :param version: version control of data.
        """
        self._module_path = module_path

    def get_data_file_path(self, data_file_path: Union[str, list, Path], data_file_filter=None) -> Union[str, list]:
        """ Get data file by version + path

        For example:
        - data_file_path is str:
            DataManager('v1').get_data_file_path('clean/100-105.json')

        - data_file_path is list:
            DataManager('v1').get_data_file_path(['clean/100-105.json', 'clean/200-105.json'])

        - data_file_path is None, data_file_filter is not None
            DataManager('v1').get_data_file_path(['clean/100-105.json', 'clean/200-105.json'])

        :param data_file_path: data file path
        """

        def __generate_completed_data_path(path: Path) -> str:
            if BaseManager.judge_version_exists(path):
                return str(path)
            else:
                raise ParameterError(f"The specified data path `{path}` does not exist.")

        if isinstance(data_file_path, str) or isinstance(data_file_path, Path):
            # path is str or path is Path
            return __generate_completed_data_path(Conf.BASE_PATH / module_path / data_file_path)
        else:
            # path is list
            return [__generate_completed_data_path(Conf.BASE_PATH / module_path / _) for _ in data_file_path]


if __name__ == '__main__':
    tmp_dir = "clean_output"
    # input data path is str
    print(DataManager(Conf.DEFAULT_VERSION).get_data_file_path(f'{tmp_dir}/100-105.json'))

    # input data path is list
    print(DataManager(Conf.DEFAULT_VERSION).get_data_file_path([f'{tmp_dir}/100-105.json', f'{tmp_dir}/200-105.json']))

    # input data path is Path
    print(DataManager(Conf.DEFAULT_VERSION).get_data_file_path(Path(f'{tmp_dir}/100-105.json')))

    # version is not exist.
    try:
        print(DataManager('v1').get_data_file_path(f'{tmp_dir}/100-105.json'))
    except ParameterError as ex:
        assert ex.args[0]['error_code'] == 'ParameterError'
        print(ex.args[0])

    # data path is not exist.
    try:
        print(DataManager(Conf.DEFAULT_VERSION).get_data_file_path(f'100-105.json'))
    except ParameterError as ex:
        assert ex.args[0]['error_code'] == 'ParameterError'
        print(ex.args[0])
