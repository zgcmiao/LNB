import os

from flask import Flask, request, jsonify, send_from_directory

from .apis import register_apis, register_logging
from .config import CONFIG_MAPPER
from .models import db
from src.dms.scheduler.task_scheduler import *

DEFAULT_ENV = 'prod'

ENV = "FLASK_ENV"

_app = Flask(__name__)


def get_runtime_env():
    """ get runtime env

    :return: env
    """
    return os.getenv(ENV) or DEFAULT_ENV


def load_config(_app, runtime_env):
    """ load config

    :param _app: core app
    :param runtime_env: runtime env by FLASK_ENV
    :return: config file
    """
    env_config_py = CONFIG_MAPPER.get(runtime_env)
    _app.config.from_pyfile(env_config_py)


def create_app():
    """ init core app

    - load config
    - register api
    - init db
    """
    load_config(_app, get_runtime_env())
    register_logging(_app)
    register_apis(_app)
    db.init_app(_app)
    with _app.app_context():
        db.create_all()
    scheduler.init_app(_app)
    scheduler.start()
    return _app


@_app.route('/')
def get_index_page(path=''):
    return _app.send_static_file('index.html')


@_app.errorhandler(404)
def page_not_found(error):
    for mime in request.accept_mimetypes:
        if mime[0] == 'text/html':
            break
        if mime[0] == 'application/json':
            return jsonify(msg='wrong url', detail='You have accessed an unknown url'), 404
    # in case we are building the front-end
    if not os.path.exists(os.path.join(_app.static_folder, 'index.html')):
        return send_from_directory(_app.root_path, 'building.html', cache_timeout=0), 503
    return _app.send_static_file('index.html'), 404
