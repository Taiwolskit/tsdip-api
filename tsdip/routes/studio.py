from flask import Blueprint, jsonify

from tsdip.models import Studio

api_blueprint = Blueprint('studios', __name__, url_prefix='/studios')


@api_blueprint.route('/', methods=['GET'])
def index():
    """ """
    return jsonify({'Data': 'Hello World'})
