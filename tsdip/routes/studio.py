from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import Schema, ValidationError, fields, validate

from tsdip.formatter import format_response
from tsdip.models import Social, Studio, RequestLog

api_blueprint = Blueprint('studios', __name__, url_prefix='/studios')


class StudioSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str()
    address = fields.Str()
    studio_type = fields.Str(
        required=True,
        validate=validate.OneOf(['dance_group', 'studio'])
    )


@api_blueprint.route('/create', methods=['POST'])
@format_response
def create():
    """
    **summary** Create a new studio.

    **description**
    @api {post} /studios/create Create a new studio
    @apiName CreateStudio
    @apiGroup Studio
    @apiDescription The API will create a studio or dance group.
    It will create a request log that needs to wait for admin approve.

    @apiParam {String} name name need to be unique
    @apiParam {String} [description] description
    @apiParam {String} [address] For studio, studio's address
    @apiParam {String[dance_group,studio]} studio_type dance_group or studio
    """
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
    name = data['name']
    description = data['description']
    address = data['address']
    studio_type = data['studio_type']

    try:
        studio = Studio(
            name=name,
            description=description,
            address=address,
            studio_type=studio_type
        )
        g.db_session.add(studio)
        g.db_session.flush()

        req_log = RequestLog(
            request='studio',
            request_id=studio.id
        )
        g.db_session.add(req_log)
        g.db_session.commit()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_STUDIO_2',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_STUDIO_1',
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }


@api_blueprint.route('', methods=['GET'])
@format_response
def get_list():
    """
    **summary** Create a new studio.

    **description**
    @api {post} /studios/create Create a new studio
    @apiName CreateStudio
    @apiGroup Studio
    @apiDescription The API will create a studio or dance group.
    It will create a request log that needs to wait for admin approve.

    @apiParam {String} name name need to be unique
    @apiParam {String} [description] description
    @apiParam {String} [address] For studio, studio's address
    @apiParam {String[dance_group,studio]} studio_type dance_group or studio
    """
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
