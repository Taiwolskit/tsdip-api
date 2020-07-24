from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from tsdip.formatter import format_response
from tsdip.models import Event, Organization, RequestEventLog, Social, User
from tsdip.schema.event import CreateEventSchema, UpdateEventSchema

api_blueprint = Blueprint('events', __name__, url_prefix='/events')


class EventException(Exception):
    """Event exception."""

    def __init__(self, comment="permission_denied"):
        """Exception constructor."""
        if comment == "org_not_exist":
            self.message = "Organization is not exist"
        elif comment == "event_not_exist":
            self.message = "Event is not exist"
        elif comment == 'permission_denied':
            self.message = "Permission denied, user doesn\'t have permission to take this action"
        else:
            self.message = "Create event exception comment empty"
        super().__init__(self.message)


def check_user_permission(roles, org_id):
    """Check user permission for the organization."""
    check_permission = False
    for role in roles:
        if role.org_id == org_id:
            check_permission = True
            break
    if not check_permission:
        raise EventException('permission_denied')
    return check_permission


@api_blueprint.route('/create', methods=['POST'])
@format_response
@jwt_required
def create_event():
    """Create event to organization with social and request log."""
    data = request.get_json()
    CreateEventSchema().load(data)
    org_id = data.get('org_id')
    org = g.db_session.query(Organization).get(org_id)
    if not org or org.deleted_at:
        raise EventException('org_not_exist')

    current_user = get_jwt_identity()
    current_user = g.db_session.query(User).get(current_user['id'])
    check_user_permission(current_user.roles, org_id)

    event = Event(org_id=org_id)
    for (key, value) in data.items():
        if key in ('name', 'description', 'amount', 'price', 'address', 'reg_link'):
            setattr(event, key, value)
        elif key in ('reg_start_at', 'reg_end_at', 'start_at', 'end_at'):
            convert_time = datetime.utcfromtimestamp(int(value) * 1e-3)
            setattr(event, key, convert_time)

    social_params = data.get('social', None)
    if social_params:
        social = Social(**social_params)
        g.db_session.add(social)
        g.db_session.flush()
        event.social_id = social.id

    g.db_session.add(event)
    g.db_session.flush()
    req_log = RequestEventLog(
        applicant_id=current_user.id,
        event_id=event.id,
        req_type='apply_event',
    )
    g.db_session.add(req_log)
    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:event_id>', methods=['GET'])
@format_response
def get_single_event(event_id):
    """Get single event detail with social."""
    event = g.db_session.query(Event).get(event_id)
    if not event or event.deleted_at:
        raise EventException('event_not_exist')

    result = event.as_dict(filter_at=True)
    result['social'] = event.social.event.as_dict(filter_at=True)
    return {
        'code': 'EVENT_API_SUCCESS',
        'data': result,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:event_id>', methods=['PUT'])
@format_response
@jwt_required
def update_event(event_id):
    """Update event with social."""
    data = request.get_json()
    UpdateEventSchema().load(data)
    current_user = get_jwt_identity()

    event = g.db_session.query(Event).get(event_id)
    if not event or event.deleted_at:
        raise EventException('event_not_exist')

    current_user = g.db_session.query(User).get(current_user['id'])
    check_user_permission(current_user.roles, event.org_id)

    for (key, value) in data.items():
        if key in ('name', 'description', 'amount', 'price', 'address', 'reg_link'):
            setattr(event, key, value)
        elif key in ('reg_start_at', 'reg_end_at', 'start_at', 'end_at'):
            convert_time = datetime.utcfromtimestamp(int(value) * 1e-3)
            setattr(event, key, convert_time)

    social_parmas = data.get('social', None)
    if social_parmas:
        if event.social:
            social = event.social
            social.update(social_parmas)
        else:
            social = Social(**social_parmas)
            g.db_session.add(social)
            g.db_session.flush()
            event.social_id = social.id

    g.db_session.add(event)
    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:event_id>', methods=['DELETE'])
@format_response
@jwt_required
def delete_event(event_id):
    """Delete event."""
    event = g.db_session.query(Event).get(event_id)
    if not event or event.deleted_at:
        raise EventException('event_not_exist')

    current_user = get_jwt_identity()
    current_user = g.db_session.query(User).get(current_user['id'])
    check_user_permission(current_user.roles, event.org_id)

    event.deleted_at = datetime.utcnow()
    g.db_session.add(event)
    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
