import json
import os

import click
from dotenv import load_dotenv
from flask import g, request
from flask.cli import with_appcontext
from flask_migrate import Migrate

from tsdip import create_app

load_dotenv()
config = 'config.DevelopmentConfig'
if os.getenv('FLASK_ENV') == 'production':
    config = 'config.ProductionConfig'

app = create_app(config=config)

if app.config['DEBUG']:
    import logging
    app.logger.setLevel(logging.DEBUG)


@app.before_request
def before_request():
    """ """
    app.logger.debug('before_request')
    app.logger.debug(f'Headers: {request.headers}')
    app.logger.debug(f'Body: {request.get_data()}')


@app.after_request
def after_request(response):
    """
    :param response:
    """
    app.logger.debug('after_request')
    app.logger.debug(f'Status: {response.status}')
    app.logger.debug(f'Headers: {response.headers}')
    app.logger.debug(f'Body: {response.get_data()}')
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    app.logger.error(f'global handle execption {e}')
    # start with the correct headers and status code from the error
    # replace the body with JSON
    response = json.dumps({
        'message': e
    })
    response.content_type = "application/json"
    return response
