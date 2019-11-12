from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import Schema, ValidationError, fields

from tsdip.formatter import format_response
from tsdip.models import Studio

api_blueprint = Blueprint('studios', __name__, url_prefix='/studios')


class StudioSchema(Schema):
    name = fields.Str(required=True)
    address = fields.Str(required=True)


@api_blueprint.route('/create', methods=['POST'])
@format_response
def create():
    """ """
    try:
        StudioSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_STUDIO_1',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

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
        return {
            'code': 'ERROR_STUDIO_2',
            'description': str(err),
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_AUTH_1',
            'data': res,
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }


@api_blueprint.route('', methods=['GET'])
@format_response
def get_list():
    params = request.args.to_dict()
    limit = int(params['limit']) if 'limit' in params and int(
        params['limit']) < 50 else 10
    page = int(params['page']) if 'page' in params and int(
        params['page']) != 0 else 1

    try:
        data = g.db_session.query(Studio) \
            .filter(Studio.deleted_at.is_(None)) \
            .order_by(Studio.name.desc()) \
            .paginate(page=page, per_page=limit)

        result = []
        while data.has_next or data.page == data.pages:
            result = result + [item.as_dict() for item in tuple(data.items)]
            data = data.next()
    except Exception as err:
        app.logger.error(err)
        return {
            'code': 'ERROR_STUDIO_3',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_AUTH_2',
            'data': result,
            'http_status_code': HTTPStatus.OK,
            'status': 'SUCCESS',
        }
