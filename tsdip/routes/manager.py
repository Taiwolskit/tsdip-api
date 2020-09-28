from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, g, request
from sqlalchemy import or_
from tsdip.auth import validate_api_token
from tsdip.formatter import format_response
from tsdip.models import (Event, Manager, Organization, RequestEventLog,
                          RequestOrgLog)
from tsdip.schema.manager import ManagerSignUpSchema

api_blueprint = Blueprint('managers', __name__, url_prefix='/managers')


class ManagerException(Exception):
    """Manager exception."""

    def __init__(self, comment):
        """Exception constructor."""
        self.message = "Manager exception comment empty"
        if comment == 'manager_data_used':
            self.message = "Manager's data have been used"

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


@api_blueprint.route('/organizations/<path:org_id>/approve', methods=['PATCH'])
@format_response
@validate_api_token
def approve_organization(org_id):
    """Approve request org log."""
    data = request.get_json()
    approve_at = datetime.utcnow()
    org = g.db_session.query(Organization).filter(
        Organization.deleted_at.is_(None),
        Organization.id == org_id
    ).one_or_none()
    if org is None:
        raise ManagerException()

    req_log = g.db_session.query(RequestOrgLog).filter(
        RequestOrgLog.org_id == org_id,
        RequestOrgLog.deleted_at.is_(None),
        RequestOrgLog.req_type == data.get('req_type')
    ).one_or_none()
    if req_log is None:
        raise ManagerException()

    req_log.approve_at = approve_at
    req_log.approver_id = g.current_user.id
    g.db_session.add(req_log)
    g.db_session.commit()

    return {
        'code': 'MANAGER_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/events/<path:event_id>/approve', methods=['PATCH'])
@format_response
@validate_api_token
def approve_event(event_id):
    """Approve request approve_event log."""
    data = request.get_json()
    approve_at = datetime.utcnow()
    event = g.db_session.query(Event).filter(
        Event.deleted_at.is_(None),
        Event.id == event_id
    ).one_or_none()
    if event is None:
        raise ManagerException()

    req_log = g.db_session.query(RequestEventLog).filter(
        RequestEventLog.event_id == event_id,
        RequestEventLog.deleted_at.is_(None),
        RequestEventLog.req_type == data.get('req_type')
    ).one_or_none()
    if req_log is None:
        raise ManagerException()

    req_log.approve_at = approve_at
    req_log.approver_id = g.current_user.id
    g.db_session.add(req_log)
    g.db_session.commit()

    return {
        'code': 'MANAGER_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
