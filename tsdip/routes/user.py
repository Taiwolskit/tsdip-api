from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from tsdip.formatter import format_response
from tsdip.models import User
from tsdip.schema.user import UserProfileSchema, UserSignUpSchema

api_blueprint = Blueprint('users', __name__, url_prefix='/users')


class UserExistException(Exception):
    """User exist exception."""

    def __init__(self, comment="user_exist"):
        """Exception constructor."""
        if comment == 'user_data_used':
            self.message = "User's data have been used"
        elif comment == 'user_not_exist':
            self.message = "User is not exist"
        else:
            self.message = "User exist exception comment empty"
        super().__init__(self.message)


def check_user_data_used(data):
    """Check email, username and telephone have been used or not."""
    email = data.get('email', None)
    username = data.get('username', None)
    telephone = data.get('telephone', None)

    or_select = []
    if email:
        email = email.lower()
        or_select.append(User.email == email)
    if username:
        username = username.lower()
        or_select.append(User.username == username)
    if telephone:
        or_select.append(User.telephone == telephone)

    exist_user = g.db_session.query(User).filter(
        or_(*or_select)
    ).one_or_none()

    if exist_user:
        raise UserExistException('user_data_used')


@api_blueprint.route('/sign_up', methods=['POST'])
@format_response
def sign_up():
    """Sign up an user."""
    data = request.get_json()
    UserSignUpSchema().load(data)
    check_user_data_used(data)
    email, username = data['email'].lower(), data['username'].lower()
    telephone = data.get('telephone', None)

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


@api_blueprint.route('/login', methods=['POST'])
@format_response
def log_in():
    """Log in an user."""
    return {
        'code': 'USER_API_SUCCESS',
        'http_status_code': HTTPStatus.ACCEPTED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/profile', methods=['PUT'])
@format_response
@jwt_required
def update_profile():
    """Update user's profile."""
    data = request.get_json()
    UserProfileSchema().load(data)

    current_user = get_jwt_identity()
    check_user_data_used(data)

    current_user = g.db_session.query(User).get(current_user['id'])
    if not current_user or current_user.deleted_at:
        raise UserExistException('user_not_exist')

    for key, value in data.items():
        setattr(current_user, key, value)
    g.db_session.add(current_user)
    g.db_session.commit()
    return {
        'code': 'USER_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/profile', methods=['GET'])
@format_response
@jwt_required
def get_profile():
    """Get user's profile."""
    current_user = get_jwt_identity()
    current_user = g.db_session.query(User).get(current_user['id'])
    profile = current_user.as_dict(filter_at=True)

    return {
        'code': 'USER_API_SUCCESS',
        'data': profile,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
