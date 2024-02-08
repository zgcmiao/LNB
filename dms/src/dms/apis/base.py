from functools import wraps

from flask import jsonify

from src.dms.exceptions.base import Error


def catch_error(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Error as e:
            return jsonify(msg=e.msg, detail=e.detail), 400

    return wrapped
