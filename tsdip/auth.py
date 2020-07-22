import os
from http import HTTPStatus

from flask import request


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
