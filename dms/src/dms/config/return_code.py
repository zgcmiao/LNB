from enum import Enum


class ReturnCode(str, Enum):
    SUCCESS = 0
    E_PARAMS = -10
