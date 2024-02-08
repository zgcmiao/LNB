# -*- coding: utf-8 -*-
from conf import Conf, ParameterError


class BaseManager:
    """ Base Manager

    """

    def __init__(self, module_name, version=("%s" % Conf.DEFAULT_VERSION),  *args, **kwargs):
        """ Init manager

        :param version: version control of data.
        """
        self._version = version
        self._module_path = module_name
        if not BaseManager.judge_version_exists(Conf.BASE_PATH / self._module_path / self._version):
            raise ParameterError(
                f"The specified version `{self._version}` under the {self._module_path} module does not exist.")

    @staticmethod
    def judge_version_exists(version_path):
        """ Judge version directory exist

        """
        return False if not version_path.exists() else True
