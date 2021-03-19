from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required)
from sqlalchemy import or_
from tsdip.auth import check_jwt_user_exist
from tsdip.formatter import format_response
from tsdip.models import Manager, User
from tsdip.schema.user import UserProfileSchema, UserSignUpSchema

api_blueprint = Blueprint('users', __name__, url_prefix='/users')


class UserException(Exception):
    """User exist exception."""

    def __init__(self, comment):
        """Exception constructor."""
        self.message = "User exist exception comment empty"
        if comment == 'user_data_used':
            self.message = "User's data have been used"

        super().__init__(self.message)


def check_user_data_used(data, user_id=None):
    """Check email, username and telephone have been used or not."""
    email = data.get('email', None)
    telephone = data.get('telephone', None)
    username = data.get('username', None)

    source_table = User
    # if g.current_user_type == 'manager':
    #     source_table = Manager

    or_select = []
    if email:
        email = email.lower()
        or_select.append(source_table.email == email)
    if telephone:
        or_select.append(source_table.telephone == telephone)
    if username:
        username = username.lower()
        or_select.append(source_table.username == username)

    exist_user = g.db_session.query(source_table).filter(
        source_table.id != user_id,
        or_(*or_select)
    ).first()

    if exist_user:
        raise UserException('user_data_used')


@api_blueprint.route('/sign_up', methods=['POST'])
@format_response
def sign_up():
    """Sign up an user."""
    # TODO: Connect to social media OAuth
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
        'http_status_code': HTTPStatus.ACCEPTED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/login', methods=['POST'])
@format_response
def log_in():
    """Log in an user."""
    # TODO: Create jwt token and return
    user = g.db_session.query(User).filter(
        User.deleted_at.is_(None)
    ).first()
    result = user.as_dict()
    result['type'] = 'user'

    return {
        'code': 'USER_API_SUCCESS',
        'data': {
            'access_token': create_access_token(identity=result, fresh=True),
            'refresh_token': create_refresh_token(identity=result)
        },
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/profile', methods=['GET'])
@format_response
@jwt_required()
@check_jwt_user_exist
def get_profile():
    """Get user's profile."""
    return {
        'code': 'USER_API_SUCCESS',
        'data': g.current_user.as_dict(filter_at=True),
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/profile', methods=['PUT'])
@format_response
@jwt_required()
@check_jwt_user_exist
def update_profile():
    """Update user's profile."""
    data = request.get_json()
    UserProfileSchema().load(data)
    user = g.current_user
    check_user_data_used(data, user.id)

    user.update(data)
    g.db_session.add(user)
    g.db_session.commit()

    return {
        'code': 'USER_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
