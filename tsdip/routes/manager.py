from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import ValidationError
from sqlalchemy import or_

from tsdip.auth import validate_api_token
from tsdip.formatter import format_response
from tsdip.models import Manager
from tsdip.schema.manager import ManagerSignUpSchema

api_blueprint = Blueprint('managers', __name__, url_prefix='/managers')


class ManagerExistException(Exception):
    """Manager exist exception."""

    def __init__(self, comment="manager_exist"):
        """Exception constructor."""
        if comment == "manager_exist":
            self.message = "Manager have been exist"
        elif comment == 'manager_data_used':
            self.message = "Manager's data have been used"
        else:
            self.message = "Manager exist exception comment empty"
        super().__init__(self.message)


@api_blueprint.route('/sign_up', methods=['POST'])
@format_response
@validate_api_token
def sign_up():
    """Sign up a manager."""
    data = request.get_json()
    ManagerSignUpSchema().load(data)

    email, username = data['email'].lower(), data['username'].lower()
    telephone = data['telephone'] if 'telephone' in data else None
    exist_manager = g.db_session.query(Manager).filter(
        or_(
            Manager.email == email,
            Manager.username == username,
        )
    ).one_or_none()

    if exist_manager:
        raise ManagerExistException('manager_data_used')
    if telephone:
        check_tel_manager = g.db_session.query(Manager).filter_by(
            telephone=telephone).one_or_none()

        if check_tel_manager:
            raise ManagerExistException('manager_data_used')

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
