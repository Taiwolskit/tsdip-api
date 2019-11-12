from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, jsonify, request
from marshmallow import Schema, ValidationError, fields

from tsdip.formatter import format_response
from tsdip.models import Studio

api_blueprint = Blueprint('studios', __name__, url_prefix='/studios')


class StudioSchema(Schema):
    name = fields.Str(required=True)
    address = fields.Str(required=True)


@api_blueprint.route('/create', methods=['POST'])
def create():
    """ """
    try:
        StudioSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        raise Exception({
            'code': 'ROUTE_AUTH_1',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        })

    data = request.get_json()
    name, address = data['name'], data['address']

    try:
        row = Studio(
            name=name,
            address=address
        )
        g.db_session.add(row)
        g.db_session.commit()
        g.db_session.flush(row)
        res = row.to_dict()
    except Exception as err:
        app.logger.error(err)
        raise Exception({
            'code': 'ROUTE_AUTH_2',
            'description': str(err),
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        })
    else:
        return format_response('ROUTE_AUTH_1', 'SUCCESS', res)
