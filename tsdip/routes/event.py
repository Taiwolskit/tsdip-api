from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import jwt_optional, jwt_required
from tsdip.auth import check_jwt_user_exist
from tsdip.formatter import format_response
from tsdip.models import (Event, RequestEventLog, Social, TicketFare, VWEventApproveStatus,
                          VWOrgApproveStatus, VWUserPermission)
from tsdip.schema.event import SocialSchema, UpdateEventSchema, TicketSchema, UpdateTicketSchema

api_blueprint = Blueprint('events', __name__, url_prefix='/events')


class EventException(Exception):
    """Event exception."""

    def __init__(self, comment):
        """Exception constructor."""
        self.message = "Event exception comment empty"
        if comment == "event_not_exist":
            self.message = "Event is not exist"
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
    event = g.db_session.query(RequestEventLog).filter(
        RequestEventLog.approve_at.isnot(None),
        RequestEventLog.deleted_at.is_(None),
        RequestEventLog.event_id == event_id,
    ).one_or_none()
    if event is None:
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
    check_user_permission(event_id, True)

    if event.social_id:
        social = event.social
        social.update(data)
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
    check_event_exist(event_id)
    check_user_permission(event_id, True)

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
    check_event_exist(event_id)
    check_user_permission(event_id, True)

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
def toggle_events_publish():
    """Toggle events publish."""
    data = request.get_json()

    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
