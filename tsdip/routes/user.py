from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from tsdip.auth import check_jwt_user_exist
from tsdip.formatter import format_response
from tsdip.models import User
from tsdip.schema.user import UserProfileSchema, UserSignUpSchema

api_blueprint = Blueprint('users', __name__, url_prefix='/users')


class UserException(Exception):
    """User exist exception."""

    def __init__(self, comment):
        """Exception constructor."""
        if comment == 'user_data_used':
            self.message = "User's data have been used"
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
        raise UserException('user_data_used')


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
@check_jwt_user_exist
def update_profile():
    """Update user's profile."""
    data = request.get_json()
    UserProfileSchema().load(data)
    check_user_data_used(data)
    current_user = g.current_user

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
@check_jwt_user_exist
def get_profile():
    """Get user's profile."""
    result = g.current_user.as_dict(filter_at=True)

    return {
        'code': 'USER_API_SUCCESS',
        'data': result,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
