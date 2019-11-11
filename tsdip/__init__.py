import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.app_context().push()
    db.init_app(app)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
