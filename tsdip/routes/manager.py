from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import Schema, ValidationError, fields

from tsdip.formatter import format_response
from tsdip.models import Manager, RequestLog

api_blueprint = Blueprint('managers', __name__, url_prefix='/managers')


class ManagerSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    telephone = fields.Str()


@api_blueprint.route('/signup', methods=['POST'])
@format_response
def create():
    try:
        ManagerSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_MANAGER_1',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    data = request.get_json()
    username, email = data['username'], data['email']
    telephone = data['telephone'] if 'telephone' in data else None

    try:
        manager = Manager(
            username=username,
            email=email,
            telephone=telephone
        )
        g.db_session.add(manager)
        g.db_session.flush()
        req_log = RequestLog(
            request='manager',
            request_id=manager.id
        )
        g.db_session.add(req_log)
        g.db_session.commit()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_MANAGER_2',
            'description': str(err),
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_MANAGER_1',
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }
