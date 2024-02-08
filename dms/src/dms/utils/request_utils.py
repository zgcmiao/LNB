import json
from functools import wraps

from flask import request
from jsonschema.validators import Draft4Validator

from src.dms.config.return_code import ReturnCode
from src.dms.utils.form_validator import FormValidator


def response_data(data=None, code=ReturnCode.SUCCESS, message='Success'):
    if data is None:
        data = {}
    return {
        "data": data,
        "code": code,
        "message": message,
    }


def response_params_error(message="invalid params"):
    return response_data(code=ReturnCode.E_PARAMS, message=message)


def parse_param_error_msg(ex):
    def format_as_index(indices):
        """
        Construct a single string containing indexing operations for the indices.

        For example, [1, 2, "foo"] -> [1][2]["foo"]

        Arguments:

            indices (sequence):

                The indices to format.

        """

        if not indices:
            return ""
        return "[%s]" % "][".join(repr(index) for index in indices)

    try:
        if "error_message" in ex.schema:
            ret = ex.schema["error_message"]
        else:
            ret = "param%s %s" % (format_as_index(ex.relative_path), ex.message)
    except:
        ret = ex.message
    return ret


def parse_params(
        form, method='GET', data_format='FORM', error_handler=response_params_error,
        check_method=True, encoding=None
):
    """
    Example:
        schema = {
            "type": "object",
            "properties": {
                "param1": {"type": "integer", "error_message": "custom error message for param1-scope error"},
                "param2": {"type": "integer"}, # default error message
            },
            "anyOf": [
                {"required": ["param1"]},
                {"required": ["param2"]},
            ],
            "error_message": "custom error message for object-scope error"
        }
        @parse_params(schema)
        def wtf(request, *args, **kwargs)
            ...

    """
    if isinstance(form, dict):
        if data_format == 'FORM':
            form = FormValidator(form)
        elif data_format == 'JSON':
            form = Draft4Validator(form)

    def wrapper(func):
        func.jsonschema = form.schema
        func.request_method = method

        @wraps(func)
        def _func(*args, **kwargs):
            if check_method and request.method != method:
                return error_handler(message="method not allowed")

            if encoding:
                request.encoding = encoding
            if method == 'POST':
                form_data = request.get_json()
            else:
                form_data = request.args

            try:
                if isinstance(form, FormValidator):
                    data = form.normalize(form_data)
                else:
                    form.validate(form_data)
                    data = form_data
            except Exception as ex:
                message = parse_param_error_msg(ex)
                return error_handler(message=message)

            return func(data, *args, **kwargs)

        return _func

    return wrapper
