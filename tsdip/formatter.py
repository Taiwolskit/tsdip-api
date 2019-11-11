import json
import traceback

from flask import current_app as app
from flask import jsonify, request

from tsdip.constants import (ErrorCode, ErrorMessage, ResponseStatus,
                             SuccessMessage)


def format_error_message(code, status='ERROR', description=None):
    """
    :param code:
    :param status:  (Default value = 'ERROR')
    """
    error_code = ErrorCode[code].value
    error_message = ErrorMessage[code].value
    error_status = ResponseStatus[status].value

    res = {
        'code': error_code,
        'description': description,
        'message': error_message,
        'status': error_status,
        'traceback': traceback.format_exc()
    }

    if app.config['DEBUG']:
        res['request'] = {
            'url': request.url,
            'body': request.get_json(),
        }
    return json.dumps(res)


def format_response(code, status='SUCCESS', data={}):
    res_status = ResponseStatus[status].value
    res_msg = SuccessMessage[code].value
    res = {
        'message': res_msg,
        'status': res_status,
        'data': data
    }

    if app.config['DEBUG']:
        res['request'] = {
            'url': request.url,
            'body': request.get_json(),
        }
    return jsonify(res)
