import os
from http import HTTPStatus

import click
from dotenv import load_dotenv
from flask import g, jsonify, request
from flask.cli import with_appcontext
from flask_migrate import Migrate
from marshmallow import ValidationError

from tsdip import create_app, db
from tsdip.formatter import format_error_message

load_dotenv()
config = 'config.DevelopmentConfig'
if os.getenv('FLASK_ENV') == 'production':
    config = 'config.ProductionConfig'

app = create_app(config=config)
migrate = Migrate(app, db)

if app.config['DEBUG']:
    import logging
    app.logger.setLevel(logging.DEBUG)


@app.before_request
def before_request():
    """Handle request before sending into the app."""
    app.logger.debug('before_request')
    app.logger.debug(f'Headers: {request.headers}')
    app.logger.debug(f'Body: {request.get_json(silent=True)}')
    g.db_session = db.session

    if 'x-request-id' in request.headers:
        g.request_id = request.headers.get('x-request-id')


@app.after_request
def after_request(response):
    """Handle response before return to the client."""
    if 'request_id' in g:
        response.headers['x-request-id'] = g.request_id
    app.logger.debug('after_request')
    app.logger.debug(f'Status: {response.status}')
    app.logger.debug(f'Headers: {response.headers}')
    app.logger.debug(f'Body: {response.get_json(silent=True)}')
    return response


@app.errorhandler(ValidationError)
def handle_schema_exception(err):
    """Handle schema exception, return JSON instead of HTML for HTTP errors."""
    app.logger.error(f'global schema exception {err}')
    app.logger.error(err.messages)
    app.logger.error(err.valid_data)
    response = format_error_message('PARAM_SCHEMA_WARN', 'WARN', err.messages)
    return jsonify(response), HTTPStatus.BAD_REQUEST


@app.errorhandler(Exception)
def handle_exception(err):
    """Handle global exception, return JSON instead of HTML for HTTP errors."""
    app.logger.error(f'global handle exception {err}')
    # start with the correct headers and status code from the error
    # replace the body with JSON
    response = format_error_message('API_FAILED', 'ERROR', str(err))
    g.db_session.rollback()
    return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


def init_db():
    """Initialize database command."""
    db.drop_all()
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


app.cli.add_command(init_db_command)
