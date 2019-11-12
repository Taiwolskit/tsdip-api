from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import Schema, ValidationError, fields

from tsdip.formatter import format_response
from tsdip.models import Social, Studio

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
        g.db_session.refresh(row)
        res = row.as_dict()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

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


class SocialSchema(Schema):
    email = fields.Email()
    fan_page = fields.Str()
    instagram = fields.Str()
    line = fields.Str()
    telephone = fields.Str()
    website = fields.URL()
    youtube = fields.Str()


@api_blueprint.route('/<path:studio_id>', methods=['PATCH'])
@format_response
def patch_social(studio_id):
    try:
        SocialSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_STUDIO_4',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    data = request.get_json()

    try:
        studio = g.db_session.query(Studio).get(studio_id)

        if not studio:
            return {
                'code': 'ERROR_STUDIO_5',
                'http_status_code': HTTPStatus.BAD_REQUEST,
                'status': 'ERROR',
            }

        row = Social(
            email=(data['email'] if 'email' in data else None),
            fan_page=(data['fan_page'] if 'fan_page' in data else None),
            instagram=(data['instagram'] if 'instagram' in data else None),
            line=(data['line'] if 'line' in data else None),
            telephone=(data['telephone'] if 'telephone' in data else None),
            website=(data['website'] if 'website' in data else None),
            youtube=(data['youtube'] if 'youtube' in data else None),
        )
        g.db_session.add(row)
        g.db_session.flush()
        studio.social_id = row.id
        g.db_session.add(studio)
        g.db_session.commit()
        res = row.as_dict()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_STUDIO_6',
            'description': str(err),
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_AUTH_3',
            'data': res,
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }
