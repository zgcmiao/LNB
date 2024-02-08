import json
import time
from functools import wraps

from flask import request


def log_request(log_response=True, max_response_length=500, log_request_body=True, max_request_body_length=None):
    def _log_request(func):
        @wraps(func)
        def _func(*args, **kwargs):
            start = time.time()
            ex = None
            try:
                response = func(*args, **kwargs)
            except Exception as e:
                ex = e
            end = time.time()
            elapsed = int((end - start) * 1000)
            if log_request_body:
                request_body = request.args
                if request.method == 'POST':
                    request_body = request.get_json()
                request_body = json.dumps(request_body)
                if max_request_body_length and len(request_body) > max_request_body_length:
                    request_body = request_body[:max_request_body_length] + '...'
            else:
                request_body = ''
            if ex is None:
                if log_response:
                    response_body = json.dumps(response)
                    if max_response_length and len(response_body) > max_response_length:
                        response_body = response_body[:max_response_length] + '...'
                else:
                    response_body = ''
            else:
                response_body = 'exception:%s' % ex
            from src.dms.app import _app
            _app.logger.info(
                'http_request|elapsed=%d,method=%s,url=%s,body=%s,response=%s',
                elapsed, request.method, request.full_path.encode('utf-8'), request_body, response_body)
            if ex is not None:
                raise ex
            return response
        return _func
    return _log_request

