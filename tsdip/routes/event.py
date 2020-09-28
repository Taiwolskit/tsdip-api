from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import jwt_required
from tsdip.auth import check_jwt_user_exist
from tsdip.formatter import format_response
from tsdip.models import (Event, Social, TicketFare, VWEventApproveStatus,
                          VWUserPermission)
from tsdip.schema.event import (SocialSchema, TicketSchema, UpdateEventSchema,
                                UpdateTicketSchema)

api_blueprint = Blueprint('events', __name__, url_prefix='/events')


class EventException(Exception):
    """Event exception."""

    def __init__(self, comment):
        """Exception constructor."""
        self.message = "Event exception comment empty"
        if comment == "event_not_exist":
            self.message = "Event is not exist"
        elif comment == "event_not_approve":
            self.message = "Event is not approved"
        elif comment == 'permission_denied':
            self.message = "Permission denied, user does not have permission to do this action"

        super().__init__(self.message)


def check_event_exist(event_id):
    """Check event exist or not."""
    event = g.db_session.query(Event).filter(
        Event.id == event_id,
        Event.deleted_at.is_(None)
    ).one_or_none()
    if event is None:
        raise EventException('event_not_exist')
    return event


def check_event_approve(event_id):
    """Check event had been approve or not."""
    # First: Check event has been approve or not.
    req_log = g.db_session.query(VWEventApproveStatus).filter(
        VWEventApproveStatus.approve_at.isnot(None),
        VWEventApproveStatus.event_id == event_id,
        VWEventApproveStatus.req_type.in_(['apply_event']),
    ).one_or_none()

    # Second: Check event have approve_at or not
    if req_log is None:
        event = check_event_exist(event_id)
        if event.approved_at is None:
            raise EventException('event_not_approve')
        return event
    else:
        raise EventException('event_not_approve')


def check_user_permission(org_id, high=False):
    """Check user has the permission for the event or not."""
    if g.current_user_type == 'manager':
        return

    data = g.db_session.query(VWUserPermission).filter(
        VWUserPermission.org_id == org_id,
        VWUserPermission.user_id == g.current_user.id,
    ).one_or_none()

    if data is None or (high and data.role not in ('owner', 'manager')):
        raise EventException('permission_denied')


@api_blueprint.route('', methods=['GET'], strict_slashes=False)
@format_response
def get_events():
    """Get events."""
    params = request.args.to_dict()
    page = params.get('page', 1)
    limit = params.get('limit', 20)

    data = g.db_session.query(Event).filter(
        Event.deleted_at.is_(None),
        Event.published_at.isnot(None)
    ).order_by(Event.name.desc())  \
        .paginate(
            error_out=False,
            max_per_page=50,
            page=int(page),
            per_page=int(limit),
    )
    result = {
        'total': data.total,
        'pages': data.pages,
        'items': [event.as_dict() for event in data.items]
    }

    return {
        'code': 'EVENT_API_SUCCESS',
        'data': result,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:event_id>', methods=['GET'])
@format_response
def get_single_event(event_id):
    """Get single event."""
    event = check_event_exist(event_id)
    check_user_permission(event.org_id)

    result = event.as_dict()
    if event.social_id:
        result['social'] = event.social.as_dict()
    result['tickets'] = [ticket.as_dict() for ticket in event.tickets]
    return {
        'code': 'EVENT_API_SUCCESS',
        'data': result,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('<path:event_id>', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_single_event(event_id):
    """Update event."""
    data = request.get_json()
    UpdateEventSchema().load(data)

    event = check_event_exist(event_id)
    check_user_permission(event.org_id)

    event.update(data)
    g.db_session.add(event)
    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:event_id>/social', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_event_social(event_id):
    """Update event's social."""
    data = request.get_json()
    SocialSchema().load(data)

    event = check_event_exist(event_id)
    check_user_permission(event.org_id, True)

    if event.social_id:
        social = event.social
        social.update(data)
        g.db_session.add(social)
    else:
        social = Social(**data)
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


@api_blueprint.route('/<path:event_id>/tickets', methods=['POST'])
@format_response
@jwt_required
@check_jwt_user_exist
def create_event_tickets(event_id):
    """Create event's tickets."""
    data = request.get_json()
    event = check_event_exist(event_id)
    check_user_permission(event.org_id, True)

    for params in data:
        TicketSchema().load(data)
        ticket = TicketFare(
            name=params['name'],
            event_id=event_id
        )
        ticket.update(params)
        g.db_session.add(ticket)

    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:event_id>/tickets', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_event_tickets(event_id):
    """Update event's tickets."""
    data = request.get_json()
    event = check_event_exist(event_id)
    check_user_permission(event.org_id, True)

    for params in data:
        UpdateTicketSchema().load(params)
        ticket = g.db_session.query(TicketFare).filter(
            TicketFare.deleted_at.is_(None),
            TicketFare.id == params['id'],
            TicketFare.event_id == event_id
        ).one_or_none()
        if ticket is None:
            continue

        ticket.update(params)
        g.db_session.add(ticket)
    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/publish', methods=['PATCH'])
@format_response
@jwt_required
@check_jwt_user_exist
def publish_events():
    """Publish events."""
    data = request.get_json()
    published_at = datetime.utcnow()

    for event_id in data:
        event = check_event_exist(event_id)
        check_user_permission(event.org_id, True)
        event.published_at = published_at
        g.db_session.add(event)

    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/un_publish', methods=['PATCH'])
@format_response
@jwt_required
@check_jwt_user_exist
def un_publish_events():
    """Publish events."""
    data = request.get_json()

    for event_id in data:
        event = check_event_exist(event_id)
        check_user_permission(event.org_id, True)
        event.published_at = None
        g.db_session.add(event)

    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
