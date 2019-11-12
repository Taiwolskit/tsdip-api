import json
import traceback

from flask import current_app as app
from flask import jsonify, request

from tsdip.constants import (ErrorCode, ErrorMessage, ResponseStatus,
                             SuccessMessage)


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


def format_response(code, status='SUCCESS', data={}):
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
    return jsonify(res)
