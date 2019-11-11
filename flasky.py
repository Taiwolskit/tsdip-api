import os

import click
from dotenv import load_dotenv
from flask import current_app, g, request
from flask_migrate import Migrate
from flask.cli import with_appcontext

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
    """

    :param e:

    """
    if isinstance(e, HTTPException):
        return e
    error = e.args[0]
    code = error['code']
    http_status_code = error['http_status_code']
    status = error['status']

    response = format_error_message(code, status)

    return Response(
        response=response,
        status=http_status_code,
        content_type="application/json"
    )


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
