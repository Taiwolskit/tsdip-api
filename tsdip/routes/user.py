from http import HTTPStatus

from flask import Blueprint, g, request
from sqlalchemy import or_

from flask_jwt_extended import get_jwt_identity, jwt_required
from tsdip.formatter import format_response
from tsdip.mail import SendGrid
from tsdip.models import Organization, RequestMemberLog, User
from tsdip.schema.user import InviteMemberSchema, UserSignUpSchema

api_blueprint = Blueprint('users', __name__, url_prefix='/users')


class UserExistException(Exception):
    """User exist exception."""

    def __init__(self, comment="user_exist"):
        """Exception constructor."""
        if comment == "user_exist":
            self.message = "User have been exist"
        elif comment == 'user_data_used':
            self.message = "User's data have been used"
        else:
            self.message = "User exist exception comment empty"
        super().__init__(self.message)


@api_blueprint.route('/sign_up', methods=['POST'])
@format_response
def sign_up():
    """Sign up an user."""
    data = request.get_json()
    UserSignUpSchema().load(data)
    email, username = data['email'].lower(), data['username'].lower()
    telephone = data['telephone'] if 'telephone' in data else None
    exist_user = g.db_session.query(User).filter(
        or_(
            User.email == email,
            User.username == username
        )
    ).one_or_none()

    if exist_user:
        raise UserExistException('user_data_used')

    if telephone:
        check_tel_manager = g.db_session.query(User).filter_by(
            telephone=telephone).one_or_none()

        if check_tel_manager:
            raise UserExistException('user_data_used')

    user = User(
        email=email,
        telephone=telephone,
        username=username,
    )
    g.db_session.add(user)
    g.db_session.commit()

    return {
        'code': 'USER_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


class InviteMemberException(Exception):
    """Invite member exception."""

    def __init__(self, comment="organization_miss"):
        """Exception constructor."""
        if comment == "organization_miss":
            self.message = "Organization is not exist"
        elif comment == 'permission_denied':
            self.message = "Permission denied, user is not have permission to invite user to this organization"
        elif comment == 'member_miss':
            self.message = 'Member is not exist'
        else:
            self.message = "Invite member exception comment empty"
        super().__init__(self.message)


@api_blueprint.route('/invite/<path:org_id>', methods=['POST'])
@format_response
# @jwt_required
def invite_member(org_id):
    """Invite member to organization."""
    org = g.db_session.query(Organization).get(org_id)
    if org is None:
        raise InviteMemberException('organization_miss')

    # current_user = get_jwt_identity()
    current_user = {
        'id': '4a750767-acab-41f6-8b6f-4e8a83edd956'
    }
    current_user = g.db_session.query(User).get(current_user['id'])
    check_permission = False
    for role in current_user.roles:
        if role.permission.could_invite and role.org_id == org_id:
            check_permission = True
            break
    if not check_permission:
        raise InviteMemberException('permission_denied')

    data = request.get_json()
    InviteMemberSchema().load(data)

    exist_member = None
    if 'user_id' in data:
        exist_member = g.db_session.query(User).get(data['user_id'])
        if exist_member is None:
            raise InviteMemberException('member_miss')
    elif 'email' in data:
        exist_member = g.db_session.query(User).filter_by(
            email=data['email'].lower()
        ).one_or_none()

    mail = SendGrid()
    if exist_member:
        req_log = RequestMemberLog(
            req_type='invite_member',
            inviter_id=current_user.id,
            invitee_id=exist_member.id,
            org_id=org_id,
        )
        g.db_session.add(req_log)
        g.db_session.commit()
        mail.send(exist_member.email, 'INVITE_EXIST_MEMBER')
    elif 'email' in data:
        req_log = RequestMemberLog(
            req_type='invite_member',
            inviter_id=current_user.id,
            email=data['email'],
            org_id=org_id,
        )
        g.db_session.add(req_log)
        g.db_session.commit()
        mail.send(data['email'], 'INVITE_MEMBER')

    return {
        'code': 'USER_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


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
