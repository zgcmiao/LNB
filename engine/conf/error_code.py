# -*- coding: utf-8 -*-

class BaseError(Exception):
    def __init__(self, error_code, message, request_id=""):
        super().__init__({"error_code": error_code, "message": message, "request_id": request_id})


class ParameterError(BaseError):
    def __init__(self, message, request_id=""):
        super().__init__("ParameterError", message, request_id)
