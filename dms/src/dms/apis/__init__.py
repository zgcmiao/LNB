import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from .task import api as task_api
from ..config import BASE_PATH


def register_apis(app: Flask):
    app.register_blueprint(task_api, url_prefix='/api/task')


def register_logging(app: Flask):
    app.logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log_path = os.path.join(BASE_PATH, 'logs')
    os.makedirs(log_path, exist_ok=True)
    file_handler = RotatingFileHandler(os.path.join(log_path, 'flask.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    if not app.debug:
        app.logger.addHandler(file_handler)
