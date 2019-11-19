from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import Schema, ValidationError, fields, validate

from tsdip.formatter import format_response
from tsdip.models import RequestLog, Social, Studio

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
    **summary** Get studio list.

    **description**
    @api {post} /studios/create Get studio list
    @apiName GetStudio
    @apiGroup Studio
    @apiDescription The API will query all studios

    @apiParam {Number{0-50}} [limit=10] limit of data rows
    @apiParam {Number{1..}} [page=1] which page start to query
    @apiParam {String[dance_group,studio]} [studio_type=studio] dance_group or studio
    """
    params = request.args.to_dict()
    limit = int(params['limit']) if 'limit' in params and int(
        params['limit']) < 50 and int(
        params['limit']) < 1 else 10
    page = int(params['page']) if 'page' in params and int(
        params['page']) < 1 else 1
    studio_type = params['studio_type'] if 'studio_type' in params else 'studio'

    try:
        data = g.db_session.query(Studio) \
            .filter(
                Studio.deleted_at.is_(None),
                Studio.studio_type == studio_type
        ) \
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
            'code': 'ROUTE_STUDIO_2',
            'data': result,
            'http_status_code': HTTPStatus.OK,
            'status': 'SUCCESS',
        }


class StudioUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    address = fields.Str()
    studio_type = fields.Str(
        validate=validate.OneOf(['dance_group', 'studio']))
    email = fields.Email()
    fan_page = fields.Str()
    instagram = fields.Str()
    line = fields.Str()
    telephone = fields.Str()
    website = fields.URL()
    youtube = fields.Str()


@api_blueprint.route('/<path:studio_id>', methods=['PUT'])
@format_response
def update(studio_id):
    """
    **summary** Update the studio.

    **description**
    @api {put} /studios/:studio_id Update the studio
    @apiName UpdateStudio
    @apiGroup Studio
    @apiDescription The API will update the studio or dance group which
    includes social data. If it haven't have social data it will create new one.

    @apiParam {String} [name] need to be unique
    @apiParam {String} [description] description about studio or dance group
    @apiParam {String} [address] For studio, studio's address
    @apiParam {String} [email] social data
    @apiParam {String} [fan_page] social data
    @apiParam {String} [instagram] social data
    @apiParam {String} [line] social data
    @apiParam {String} [telephone] social data
    @apiParam {String} [website] social data
    @apiParam {String} [youtube] social data
    """
    try:
        StudioUpdateSchema().load(request.get_json())
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

        social = studio.social if studio.social else Social()

        for (key, value) in data.items():
            # studio
            if key in ('name', 'description'):
                setattr(studio, key, value)
            # social
            elif key in ('email', 'fan_page', 'instagram', 'line', 'telephone', 'website', 'youtube'):
                setattr(social, key, value)
            elif key == 'address' and studio.studio_type == 'studio':
                setattr(studio, key, value)

        g.db_session.add(social)
        g.db_session.flush()
        studio.social_id = social.id
        g.db_session.add(studio)
        g.db_session.commit()
        res = studio.as_dict()
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
            'code': 'ROUTE_STUDIO_3',
            'data': res,
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }
