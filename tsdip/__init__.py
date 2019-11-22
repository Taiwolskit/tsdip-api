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

    from .routes.event import api_blueprint as event_blueprint
    from .routes.manager import api_blueprint as manager_blueprint
    from .routes.studio import api_blueprint as studio_blueprint

    app.register_blueprint(event_blueprint)
    app.register_blueprint(manager_blueprint)
    app.register_blueprint(studio_blueprint)

    return app
