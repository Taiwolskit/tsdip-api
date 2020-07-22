from http import HTTPStatus

from flask import Blueprint, g, request

from flask_jwt_extended import get_jwt_identity, jwt_required
from tsdip.formatter import format_response
from tsdip.models import Organization, RequestOrgLog, Social
from tsdip.schema.org import CreateOrgSchema

api_blueprint = Blueprint('orgs', __name__, url_prefix='/orgs')


@api_blueprint.route('/create', methods=['POST'])
@format_response
@jwt_required
def create_org():
    """Create organization with request log."""
    data = request.get_json()
    CreateOrgSchema().load(data)
    current_user = get_jwt_identity['id']
    name = data['name']
    org_type = data['org_type']

    description = data.get('description', None)
    address = data.get('address', None)
    social_params = data.get('social', None)

    org = Organization(
        address=address,
        description=description,
        name=name,
        org_type=org_type
    )
    g.db_session.add(org)
    g.db_session.flush()

    if social_params:
        social = Social(**social_params)
        g.db_session.add(social)
        g.db_session.flush()
        org.social_id = social.id

    req_log = RequestOrgLog(
        req_type='apply_org',
        org_id=org.id,
        applicant_id=current_user['id']
    )
    g.db_session.add(req_log)
    g.db_session.commit()

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


# @api_blueprint.route('', methods=['GET'])
# @format_response
# def get_list():
#     """
#     **summary** Get studio list.

#     **description**
#     @api {post} /studios/create Get studio list
#     @apiName GetStudio
#     @apiGroup Studio
#     @apiDescription The API will query all studios

#     @apiParam {Number{0-50}} [limit=10] limit of data rows
#     @apiParam {Number{1..}} [page=1] which page start to query
#     @apiParam {String[dance_group,studio]} [studio_type=studio] dance_group or studio
#     """
#     params = request.args.to_dict()
#     limit = int(params['limit']) if 'limit' in params and int(
#         params['limit']) < 50 and int(
#         params['limit']) < 1 else 10
#     page = int(params['page']) if 'page' in params and int(
#         params['page']) < 1 else 1
#     studio_type = params['studio_type'] if 'studio_type' in params else 'studio'

#     try:
#         data = g.db_session.query(Studio).join(
#             RequestLog,
#             RequestLog.request_id == Studio.id,
#         ) \
#             .filter(
#                 RequestLog.approve == true(),
#                 RequestLog.approve_at.isnot(None),
#                 RequestLog.request == 'studio',
#                 Studio.deleted_at.is_(None),
#                 Studio.studio_type == studio_type,
#         ) \
#             .order_by(Studio.name.desc()) \
#             .paginate(page=page, per_page=limit)

#         result = []
#         while data.has_next or data.page == data.pages:
#             result = result + [item.as_dict() for item in tuple(data.items)]
#             data = data.next()
#     except Exception as err:
#         app.logger.error(err)
#         return {
#             'code': 'ERROR_STUDIO_3',
#             'description': str(err),
#             'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
#             'status': 'ERROR',
#         }
#     else:
#         return {
#             'code': 'ROUTE_STUDIO_2',
#             'data': result,
#             'http_status_code': HTTPStatus.OK,
#             'status': 'SUCCESS',
#         }


# class SocialSchema(Schema):
#     email = fields.Email()
#     fan_page = fields.URL()
#     instagram = fields.Str()
#     line = fields.Str()
#     telephone = fields.Str()
#     website = fields.URL()
#     youtube = fields.URL()


# class StudioUpdateSchema(Schema):
#     name = fields.Str()
#     description = fields.Str()
#     address = fields.Str()
#     studio_type = fields.Str(
#         validate=validate.OneOf(['dance_group', 'studio']))

#     social = fields.Nested(SocialSchema)


# @api_blueprint.route('/<path:studio_id>', methods=['PUT'])
# @format_response
# def update(studio_id):
#     """
#     **summary** Update the studio.

#     **description**
#     @api {put} /studios/:studio_id Update the studio
#     @apiName UpdateStudio
#     @apiGroup Studio
#     @apiDescription The API will update the studio or dance group which
#     includes social data. If it haven't have social data it will create new one.

#     @apiParam {String} [name] need to be unique
#     @apiParam {String} [description] description about studio or dance group
#     @apiParam {String} [address] For studio, studio's address
#     @apiParam {String} [social.email] social data
#     @apiParam {String} [social.fan_page] social data
#     @apiParam {String} [social.instagram] social data
#     @apiParam {String} [social.line] social data
#     @apiParam {String} [social.telephone] social data
#     @apiParam {String} [social.website] social data
#     @apiParam {String} [social.youtube] social data
#     """
#     try:
#         StudioUpdateSchema().load(request.get_json())
#     except ValidationError as err:
#         app.logger.error(err.messages)
#         app.logger.error(err.valid_data)
#         return {
#             'code': 'ERROR_STUDIO_4',
#             'description': err.messages,
#             'http_status_code': HTTPStatus.BAD_REQUEST,
#             'status': 'ERROR',
#         }

#     data = request.get_json()

#     try:
#         studio = g.db_session.query(Studio).get(studio_id)

#         if not studio or studio.deleted_at:
#             return {
#                 'code': 'ERROR_STUDIO_5',
#                 'http_status_code': HTTPStatus.BAD_REQUEST,
#                 'status': 'ERROR',
#             }

#         social = studio.social if studio.social else Social()
#         have_social = False

#         for (key, value) in data.items():
#             # studio
#             if key in ('name', 'description'):
#                 setattr(studio, key, value)
#             elif key == 'address' and studio.studio_type == 'studio':
#                 setattr(studio, key, value)
#             # social
#             elif key == 'social':
#                 for (social_key, social_value) in value.items():
#                     if social_key in ('email', 'fan_page', 'instagram', 'line', 'telephone',
#                                       'website', 'youtube'):
#                         have_social = True
#                         setattr(social, social_key, social_value)

#         if have_social:
#             g.db_session.add(social)
#             g.db_session.flush()
#             studio.social_id = social.id

#         g.db_session.add(studio)
#         g.db_session.commit()
#         res = studio.as_dict()
#     except Exception as err:
#         app.logger.error(err)
#         g.db_session.rollback()

#         return {
#             'code': 'ERROR_STUDIO_6',
#             'description': str(err),
#             'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
#             'status': 'ERROR',
#         }
#     else:
#         return {
#             'code': 'ROUTE_STUDIO_3',
#             'data': res,
#             'http_status_code': HTTPStatus.OK,
#             'status': 'SUCCESS',
#         }


# @api_blueprint.route('/<path:studio_id>', methods=['DELETE'])
# @format_response
# def delete(studio_id):
#     """
#     **summary** Delete the studio.

#     **description**
#     @api {put} /studios/:studio_id Delete the studio
#     @apiName DeleteStudio
#     @apiGroup Studio
#     @apiDescription The API will delete the studio or dance group.
#     It also will delete all events which is created by this studio or dance group.
#     """
#     try:
#         studio = g.db_session.query(Studio).get(studio_id)

#         if not studio or studio.deleted_at:
#             return {
#                 'code': 'ERROR_STUDIO_7',
#                 'http_status_code': HTTPStatus.BAD_REQUEST,
#                 'status': 'ERROR',
#             }

#         for event in studio.events:
#             event.deleted_at = datetime.utcnow()
#             g.db_session.add(event)

#         studio.deleted_at = datetime.utcnow()
#         g.db_session.add(studio)
#         g.db_session.commit()
#     except Exception as err:
#         app.logger.error(err)
#         g.db_session.rollback()

#         return {
#             'code': 'ERROR_STUDIO_8',
#             'description': str(err),
#             'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
#             'status': 'ERROR',
#         }
#     else:
#         return {
#             'code': 'ROUTE_STUDIO_4',
#             'http_status_code': HTTPStatus.OK,
#             'status': 'SUCCESS',
#         }
