import json
import traceback

from flask import current_app as app
from flask import request

from tsdip.constants import ErrorCode, ErrorMessage, ResponseStatus


def format_error_message(code, status='ERROR'):
    """

    :param code:
    :param status:  (Default value = 'ERROR')

    """
    error_status = ResponseStatus[status].value
    error_code = ErrorCode[code].value
    error_message = ErrorMessage[code].value

    res = {
        'status': error_status,
        'code': error_code,
        'message': error_message,
        'traceback': traceback.format_exc()
    }

    if app.config['DEBUG']:
        res['request'] = {
            'url': request.url,
            'body': request.get_json(),
        }
    return json.dumps(res)
