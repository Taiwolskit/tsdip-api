import os

from flask import Flask, jsonify

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.app_context().push()

    @app.route('/hello')
    def hello_world():
        return jsonify({'text': 'Hello, World!'})

    return app
