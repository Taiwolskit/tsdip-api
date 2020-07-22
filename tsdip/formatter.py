import traceback
from http import HTTPStatus

from flask import current_app as app
from flask import jsonify, request

from tsdip.constants import (ErrorCode, ErrorMessage, ResponseStatus,
                             SuccessMessage)


def format_response(fn):
    """Format API response structure."""

    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)

        if 'status' in res:
            code = res.get('code', 'DEFAULT_ERROR')
            http_status_code = res.get(
                'http_status_code', HTTPStatus.INTERNAL_SERVER_ERROR)
            status = res.get('status', 'ERROR')

            if status in ('ERROR', 'WARN'):
                description = res.get('description', None)
                response = format_error_message(code, status, description)
                return jsonify(response), http_status_code

            data = res.get('data', None)
            response = format_success_response(code, status, data)
            return jsonify(response), http_status_code

        response = format_error_message('DEFAULT_ERROR')
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR

    wrapper.__name__ = fn.__name__
    return wrapper


def format_error_message(code, status='ERROR', description=None):
    """Format API error response.

    Args:
        code (str): Custom Error Code
        status (str): API status (Default value = 'ERROR')
        description (str): error extra description (Default value = None)
    """
    res_code = ErrorCode(code).value
    res_msg = ErrorMessage(code).value
    res_status = ResponseStatus(status).value

    res = {
        'code': res_code,
        'message': res_msg,
        'status': res_status,
    }
    if description:
        res['description'] = description

    if app.config['DEBUG']:
        res['traceback'] = traceback.format_exc()
        res['request'] = {
            'url': request.url,
            'body': request.get_json(),
        }
    return res


def format_success_response(code, status='SUCCESS', data=None):
    """Format API success response.

    Args:
        code (str): Custom Success Code
        status (str): API status (Default value = 'SUCCESS')
        data (str): API response data (Default value = None)
    """
    res_status = ResponseStatus(status).value
    res_msg = SuccessMessage(code).value
    res = {
        'message': res_msg,
        'status': res_status,
    }

    if data:
        res['data'] = data

    if app.config['DEBUG']:
        res['request'] = {
            'url': request.url,
            'body': request.get_json(silent=True),
        }

    return res
