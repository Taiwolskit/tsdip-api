import json
import os

import click
from dotenv import load_dotenv
from flask import g, request
from flask.cli import with_appcontext
from flask_migrate import Migrate

from tsdip import create_app, db

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
    """ """
    app.logger.debug('before_request')
    app.logger.debug(f'Headers: {request.headers}')
    app.logger.debug(f'Body: {request.get_data()}')
    g.db_session = db.session


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
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


def init_db():
    """ """
    db.drop_all()
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


app.cli.add_command(init_db_command)
