from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import ValidationError
from sqlalchemy import or_

from tsdip.formatter import format_response
from tsdip.models import Manager
from tsdip.schema.manager import ManagerSignUpSchema

api_blueprint = Blueprint('managers', __name__, url_prefix='/managers')


class ManagerExist(Exception):
    def __init__(self, comment="manager_exist"):
        if comment == "manager_exist":
            self.message = "Manager have been exist"
        elif comment == 'manager_data_used':
            self.message = "Manager's data have been used"
        else:
            self.message = "Manage exist exception comment empty"
        super().__init__(self.message)


@api_blueprint.route('/signup', methods=['POST'])
@format_response
def sign_up():
    # step1: API TOKEN 有效性
    try:
        data = request.get_json()
        ManagerSignUpSchema.load(data)
        managers = g.db_session.query(Manager).filter(
            or_(
                Manager.username == data['username'],
                Manager.email == data['email']
            )
        ).first()

        if len(managers) > 0:
            raise ManagerExist('manager_data_used')

        manager = Manager(
            username=data['username'],
            email=data['email']
        )

        if 'telephone' in data:
            check_tel_manager = g.db_session.query(Manager).filter_by(
                telephone=data['telephone']).first()

            if check_tel_manager:
                raise ManagerExist('manager_data_used')

            manager.telephone = data['telephone']

        g.db_session.add(manager)
        g.db_session.commit()
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)

        return {
            'code': 'WARN_MANAGER_SCHEMA',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'WARN',
        }
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_MANAGER_SIGNUP',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'SUCCESS_MANAGER_SIGNUP',
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }


# class ManagerSchema(Schema):
#     email = fields.Email(required=True)
#     telephone = fields.Str()
#     username = fields.Str(required=True)


# @api_blueprint.route('/signup', methods=['POST'])
# @format_response
# def create():
#     """
#     **summary** Sign Up new a manager.

#     **description**
#     @api {post} /managers/signup Sign Up new a manager
#     @apiName CreateManager
#     @apiGroup Manager
#     @apiDescription Sign Up a new manager which haven't been invited by
#     another studio before. This API will create a manager and a request log
#     which needs to be approved by admin. Once admin approves, the manager
#     will start to use and create a studio.

#     @apiParam {String} [telephone] User's telephone
#     @apiParam {String} email User's email, need to be unique
#     @apiParam {String} username User's username, need to be unique
#     """
#     try:
#         ManagerSchema().load(request.get_json())
#     except ValidationError as err:
#         app.logger.error(err.messages)
#         app.logger.error(err.valid_data)
#         return {
#             'code': 'ERROR_MANAGER_1',
#             'description': err.messages,
#             'http_status_code': HTTPStatus.BAD_REQUEST,
#             'status': 'ERROR',
#         }

#     data = request.get_json()
#     email, username = data['email'], data['username']
#     telephone = data['telephone'] if 'telephone' in data else None

#     try:
#         exist_manager = g.db_session.query(Manager).filter(
#             or_(
#                 Manager.email == email,
#                 Manager.username == username
#             )
#         ).one_or_none()
#         if exist_manager:
#             return {
#                 'code': 'ERROR_MANAGER_2',
#                 'http_status_code': HTTPStatus.BAD_REQUEST,
#                 'status': 'ERROR',
#             }

#         manager = Manager(
#             email=email,
#             telephone=telephone,
#             username=username,
#         )
#         g.db_session.add(manager)
#         g.db_session.flush()

#         req_log = RequestLog(
#             request='manager',
#             request_id=manager.id
#         )
#         g.db_session.add(req_log)
#         g.db_session.commit()
#     except Exception as err:
#         app.logger.error(err)
#         g.db_session.rollback()

#         return {
#             'code': 'ERROR_MANAGER_3',
#             'description': str(err),
#             'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
#             'status': 'ERROR',
#         }
#     else:
#         return {
#             'code': 'ROUTE_MANAGER_1',
#             'http_status_code': HTTPStatus.CREATED,
#             'status': 'SUCCESS',
#         }


# @api_blueprint.route('/invite/<path:studio_id>', methods=['POST'])
# @format_response
# def invite(studio_id):
#     """
#     **summary** Invite a manager.

#     **description**
#     @api {post} /managers/invite/:studio_id Invite a manager
#     @apiName InviteManager
#     @apiGroup Manager
#     @apiDescription This API will invite a manager to manage the studio.
#     If this manager hasn't signed up, this will create a new manager.
#     After both of these, it will create a new request log and
#     send an email to wait for confirmation.

#     @apiParam {String} [telephone] User's telephone
#     @apiParam {String} email User's email, need to be unique
#     @apiParam {String} username User's username, need to be unique
#     """
#     try:
#         ManagerSchema().load(request.get_json())
#     except ValidationError as err:
#         app.logger.error(err.messages)
#         app.logger.error(err.valid_data)
#         return {
#             'code': 'ERROR_MANAGER_4',
#             'description': err.messages,
#             'http_status_code': HTTPStatus.BAD_REQUEST,
#             'status': 'ERROR',
#         }

#     mail = SendGrid()
#     data = request.get_json()
#     email, username = data['email'], data['username']
#     telephone = data['telephone'] if 'telephone' in data else None

#     try:
#         studio = g.db_session.query(Studio).get(studio_id)
#         if not studio or studio.deleted_at:
#             return {
#                 'code': 'ERROR_MANAGER_5',
#                 'http_status_code': HTTPStatus.BAD_REQUEST,
#                 'status': 'ERROR',
#             }

#         manager = g.db_session.query(Manager).filter(
#             Manager.deleted_at.is_(None),
#             Manager.email == email,
#             Manager.username == username,
#         ).one_or_none()

#         if manager:
#             manager.studios.append(studio)
#         else:
#             manager = Manager(
#                 email=email,
#                 telephone=telephone,
#                 username=username,
#             )
#             g.db_session.add(manager)
#             g.db_session.flush()
#             manager.studios.append(studio)

#         req_log = RequestLog(
#             request='invite',
#             request_id=manager.id
#         )
#         g.db_session.add(req_log)
#         g.db_session.commit()
#     except Exception as err:
#         app.logger.error(err)
#         g.db_session.rollback()

#         return {
#             'code': 'ERROR_MANAGER_6',
#             'description': str(err),
#             'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
#             'status': 'ERROR',
#         }
#     else:
#         mail.send(email)
#         return {
#             'code': 'ROUTE_MANAGER_2',
#             'http_status_code': HTTPStatus.CREATED,
#             'status': 'SUCCESS',
#         }


# class ManagerUpdateSchema(Schema):
#     email = fields.Email()
#     telephone = fields.Str()
#     username = fields.Str()


# @api_blueprint.route('/<path:manager_id>', methods=['PUT'])
# @format_response
# def update(manager_id):
#     """
#     **summary** Update a manager's profile.

#     **description**
#     @api {put} /managers/:manager_id Update a manager's profile
#     @apiName UpdateManagerProfile
#     @apiGroup Manager
#     @apiDescription The API will update a manager's profile.
#     Email and username need to be unique.

#     @apiParam {String} [telephone] User's telephone
#     @apiParam {String} [email] User's email, need to be unique
#     @apiParam {String} [username] User's username, need to be unique
#     """
#     try:
#         ManagerUpdateSchema().load(request.get_json())
#     except ValidationError as err:
#         app.logger.error(err.messages)
#         app.logger.error(err.valid_data)
#         return {
#             'code': 'ERROR_MANAGER_7',
#             'description': err.messages,
#             'http_status_code': HTTPStatus.BAD_REQUEST,
#             'status': 'ERROR',
#         }

#     data = request.get_json()

#     try:
#         manager = g.db_session.query(Manager).get(manager_id)
#         if not manager or manager.deleted_at:
#             return {
#                 'code': 'ERROR_MANAGER_8',
#                 'http_status_code': HTTPStatus.BAD_REQUEST,
#                 'status': 'ERROR',
#             }

#         for (key, value) in data.items():
#             setattr(manager, key, value)

#         g.db_session.add(manager)
#         g.db_session.commit()
#     except Exception as err:
#         app.logger.error(err)
#         g.db_session.rollback()

#         return {
#             'code': 'ERROR_MANAGER_9',
#             'description': str(err),
#             'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
#             'status': 'ERROR',
#         }
#     else:
#         return {
#             'code': 'ROUTE_MANAGER_3',
#             'http_status_code': HTTPStatus.ACCEPTED,
#             'status': 'SUCCESS',
#         }


# class ManagerPermissionSchema(Schema):
#     role = fields.Str(
#         required=True,
#         validate=validate.OneOf(['break', 'manager', 'owner', 'viewer'])
#     )
#     studio_id = fields.UUID(required=True)


# @api_blueprint.route('/permission/<path:manager_id>', methods=['PUT'])
# @format_response
# def update_permission(manager_id):
#     """
#     **summary** Update a manager's permission.

#     **description**
#     @api {put} /managers/permission/:manager_id Update a manager's permission.
#     @apiName UpdateManagerPermission
#     @apiGroup Manager
#     @apiDescription This API will invite a manager to manage the studio.
#     If this manager hasn't signed up, this will create a new manager.
#     After both of these, it will create a new request log and
#     send an email to wait for confirmation.

#     @apiParam {String} role The role which the manager will change to
#     @apiParam {String} studio_id The manager will change which studio role
#     """
#     try:
#         ManagerPermissionSchema().load(request.get_json())
#     except ValidationError as err:
#         app.logger.error(err.messages)
#         app.logger.error(err.valid_data)
#         return {
#             'code': 'ERROR_MANAGER_10',
#             'description': err.messages,
#             'http_status_code': HTTPStatus.BAD_REQUEST,
#             'status': 'ERROR',
#         }

#     data = request.get_json()
#     role, studio_id = data['role'], data['studio_id']

#     try:
#         manager = g.db_session.query(Manager).get(manager_id)
#         if not manager and manager.deleted_at:
#             return {
#                 'code': 'ERROR_MANAGER_11',
#                 'http_status_code': HTTPStatus.BAD_REQUEST,
#                 'status': 'ERROR',
#             }

#         studio = g.db_session.query(Studio).get(studio_id)
#         if not studio and studio.deleted_at:
#             return {
#                 'code': 'ERROR_MANAGER_12',
#                 'http_status_code': HTTPStatus.BAD_REQUEST,
#                 'status': 'ERROR',
#             }

#         if role == 'break':
#             manager.studios.remove(studio)
#         else:
#             g.db_session.execute(
#                 """
#                 UPDATE permission
#                 SET role = :role
#                 WHERE manager_id = :manager_id
#                     AND studio_id = :studio_id
#                 """,
#                 {
#                     'manager_id': manager_id,
#                     'role': role,
#                     'studio_id': studio_id
#                 }
#             )
#         g.db_session.commit()
#     except Exception as err:
#         app.logger.error(err)
#         return {
#             'code': 'ERROR_MANAGER_13',
#             'description': str(err),
#             'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
#             'status': 'ERROR',
#         }
#     else:
#         return {
#             'code': 'ROUTE_MANAGER_4',
#             'http_status_code': HTTPStatus.OK,
#             'status': 'SUCCESS',
#         }
