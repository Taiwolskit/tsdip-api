from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from flask_jwt_extended import JWTManager

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)


def create_app(config=None):
    """Create flask context app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.app_context().push()

    db.init_app(app)
    JWTManager(app)

    from .routes.event import api_blueprint as event_blueprint
    from .routes.manager import api_blueprint as manager_blueprint
    from .routes.org import api_blueprint as org_blueprint
    from .routes.user import api_blueprint as user_blueprint

    app.register_blueprint(event_blueprint)
    app.register_blueprint(manager_blueprint)
    app.register_blueprint(org_blueprint)
    app.register_blueprint(user_blueprint)

    @app.route('/hello')
    def hello_world():
        return jsonify({'text': 'Hello, World!'})

    return app
