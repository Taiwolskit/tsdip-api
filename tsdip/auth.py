import os
from http import HTTPStatus

from flask import g, request
from flask_jwt_extended import get_jwt_identity

from tsdip.models import Manager, User


def validate_api_token(fn):
    """Validate API token at request header."""

    def wrapper(*args, **kwargs):
        token = request.headers.get('x-api-token', None)

        if token != os.getenv('API_TOKEN'):
            return {
                'code': 'AUTH_API_TOKEN_ERROR',
                'http_status_code': HTTPStatus.FORBIDDEN,
                'status': 'WARN',
            }
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


def check_jwt_user_exist(fn):
    """Validate JWT token, check the user exist or not."""

    def wrapper(*args, **kwargs):
        # current_user = get_jwt_identity()
        source_table = User
        # if current_user['type'] == 'manager':
        #     source_table = Manager

        query_user = g.db_session.query(source_table).filter(
            source_table.id == '5cc1804d-1ab3-4a90-9f33-87af947b5e51',
            source_table.deleted_at.is_(None)
        ).one_or_none()
        if query_user is None:
            return {
                'code': 'JWT_INVALID',
                'http_status_code': HTTPStatus.FORBIDDEN,
                'status': 'WARN',
            }
        g.current_user = query_user
        # g.current_user_type = current_user['type']
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper
