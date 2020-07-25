from http import HTTPStatus

from flask import Blueprint, g, request
from sqlalchemy import or_

from tsdip.auth import validate_api_token
from tsdip.formatter import format_response
from tsdip.models import Manager
from tsdip.schema.manager import ManagerSignUpSchema

api_blueprint = Blueprint('managers', __name__, url_prefix='/managers')


class ManagerException(Exception):
    """Manager exception."""

    def __init__(self, comment):
        """Exception constructor."""
        if comment == 'manager_data_used':
            self.message = "Manager's data have been used"
        else:
            self.message = "Manager exception comment empty"
        super().__init__(self.message)


def check_manager_data_used(data):
    """Check email, username and telephone have been used or not."""
    email = data.get('email', None)
    username = data.get('username', None)
    telephone = data.get('telephone', None)

    or_select = []
    if email:
        email = email.lower()
        or_select.append(Manager.email == email)
    if username:
        username = username.lower()
        or_select.append(Manager.username == username)
    if telephone:
        or_select.append(Manager.telephone == telephone)

    exist_user = g.db_session.query(Manager).filter(
        or_(*or_select)
    ).one_or_none()

    if exist_user:
        raise ManagerException('manager_data_used')


@api_blueprint.route('/sign_up', methods=['POST'])
@format_response
@validate_api_token
def sign_up():
    """Sign up a manager."""
    data = request.get_json()
    ManagerSignUpSchema().load(data)
    check_manager_data_used(data)
    email, username = data['email'].lower(), data['username'].lower()
    telephone = data.get('telephone', None)

    manager = Manager(
        email=email,
        telephone=telephone,
        username=username,
    )
    g.db_session.add(manager)
    g.db_session.commit()

    return {
        'code': 'MANAGER_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }
