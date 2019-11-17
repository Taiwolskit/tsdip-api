import json
import traceback
from http import HTTPStatus

from flask import Response
from flask import current_app as app
from flask import jsonify, request

from tsdip.constants import (ErrorCode, ErrorMessage, ResponseStatus,
                             SuccessMessage)


def format_response(fn):
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)

        if 'status' in res:
            if res['status'] == 'ERROR':
                code = res['code']
                description = res['description'] if 'description' in res else None
                http_status_code = res['http_status_code']
                status = res['status']

                response = format_error_message(code, status, description)
                return Response(
                    content_type="application/json",
                    response=response,
                    status=http_status_code,
                )
            else:
                code = res['code']
                data = res['data'] if 'data' in res else {}
                http_status_code = res['http_status_code']
                status = res['status']

                response = format_success_response(code, status, data)
                return jsonify(response), http_status_code
        else:
            response = format_error_message('ROUTE_AUTH_0')
            return Response(
                content_type="application/json",
                response=response,
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
    wrapper.__name__ = fn.__name__
    return wrapper


def format_error_message(code, status='ERROR', description=None):
    """
    :param code: Custom Error Code
    :param status: api status (Default value = 'ERROR')
    :param description: error extra description (Default value = None)
    """
    error_code = ErrorCode[code].value
    error_message = ErrorMessage[code].value
    error_status = ResponseStatus[status].value

    res = {
        'code': error_code,
        'description': description,
        'message': error_message,
        'status': error_status,
    }

    if app.config['DEBUG']:
        res['traceback'] = traceback.format_exc()
        res['request'] = {
            'url': request.url,
            'body': request.get_json(),
        }
    return json.dumps(res)


def format_success_response(code, status='SUCCESS', data={}):
    """
    :param code: Custom Success Code
    :param status: api status (Default value = 'SUCCESS')
    :param data: api request data (Default value = {})
    """
    res_status = ResponseStatus[status].value
    res_msg = SuccessMessage[code].value
    res = {
        'data': data,
        'message': res_msg,
        'status': res_status,
    }

    if app.config['DEBUG']:
        res['request'] = {
            'url': request.url,
            'body': request.get_json(),
        }

    return res
