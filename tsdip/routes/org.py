from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import jwt_required
from tsdip.auth import check_jwt_user_exist
from tsdip.formatter import format_response
from tsdip.mail import SendGrid
from sqlalchemy import select
from tsdip.models import (Event, Organization, RequestEventLog, Role, user_role,
                          RequestMemberLog, RequestOrgLog, Social, TicketFare,
                          User, VWUserPermission)
from tsdip.schema.org import (CreateEventSchema, CreateOrgSchema,
                              InviteMemberSchema, UpdateEventSchema,
                              UpdateOrgSchema)

api_blueprint = Blueprint('organizations', __name__,
                          url_prefix='/organizations')


class OrganizationException(Exception):
    """Invite member exception."""

    def __init__(self, comment):
        """Exception constructor."""
        self.message = "Organization exception comment empty"

        if comment == "organization_not_exist":
            self.message = "Organization is not exist"
        elif comment == "organization_not_approve":
            self.message = "Organization is not approved"
        elif comment == 'permission_denied':
            self.message = "Permission denied, user does not have permission to do this action"
        elif comment == 'member_not_exist':
            self.message = 'Member is not exist'

        super().__init__(self.message)


class EventException(Exception):
    """Event exception."""

    def __init__(self, comment):
        """Exception constructor."""
        self.message = "Event exception comment empty"

        if comment == "event_not_exist":
            self.message = "Event is not exist"

        super().__init__(self.message)


def check_org_exist(org_id):
    """Check organization exist or not."""
    org = g.db_session.query(Organization).filter(
        Organization.id == org_id,
        Organization.deleted_at.is_(None)
    ).one_or_none()
    if org is None:
        raise OrganizationException('organization_not_exist')
    return org


def check_event_exist(org_id, event_id):
    """Check organization's event exist or not."""
    event = g.db_session.query(Event).filter(
        Event.id == event_id,
        Event.org_id == org_id,
        Event.deleted_at.is_(None)
    ).one_or_none()
    if event is None:
        raise EventException('event_not_exist')
    return event


def check_org_approve(org_id):
    """Check organization had been approve or not."""
    org = g.db_session.query(RequestOrgLog).filter(
        RequestOrgLog.approve_at.isnot(None),
        RequestOrgLog.deleted_at.is_(None),
        RequestOrgLog.org_id == org_id,
        RequestOrgLog.req_type.in_,
    ).one_or_none()
    if org is None:
        raise OrganizationException('organization_not_approve')


def check_user_permission(org_id, high=False):
    """Check user has the permission for the organization or not."""
    if g.current_user_type == 'manager':
        return

    data = g.db_session.query(VWUserPermission).filter(
        VWUserPermission.org_id == org_id,
        VWUserPermission.user_id == g.current_user.id,
    ).one_or_none()

    if data is None or (high and data.role not in ('owner', 'manager')):
        raise OrganizationException('permission_denied')


@api_blueprint.route('/create', methods=['POST'])
@format_response
@jwt_required
@check_jwt_user_exist
def create_org():
    """Create organization with social and request log.

    This API will have two situations.
    First: General user create the organization,
        it will create request log
    Second: Manager create the organization,
        it will not create request log
    The user permission will create until the request has been approved
    """
    data = request.get_json()
    CreateOrgSchema().load(data)

    description = data.get('description', None)
    name = data.get('name')
    org_type = data.get('org_type')
    social_params = data.get('social', None)

    org = Organization(
        description=description,
        name=name,
        org_type=org_type
    )
    g.db_session.add(org)
    g.db_session.flush()

    if social_params:
        social = Social(**social_params)
        g.db_session.add(social)
        g.db_session.flush()
        org.social_id = social.id

    if g.current_user_type == 'user':
        req_log = RequestOrgLog(
            applicant_id=g.current_user.id,
            org_id=org.id,
            req_type='apply_org',
        )
        g.db_session.add(req_log)

    g.db_session.commit()

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/', methods=['GET'])
@format_response
@jwt_required
@check_jwt_user_exist
def get_orgs():
    """Get organization list.

    This API only provider for managers
    """
    params = request.args.to_dict()
    page = params.get('page', 1)
    limit = params.get('limit', 20)

    if g.current_user_type != 'manager':
        raise OrganizationException('permission_denied')

    data = g.db_session.query(Organization).filter(
        Organization.deleted_at.is_(None)
    ).order_by(Organization.created_at.desc())  \
        .paginate(
            error_out=False,
            max_per_page=50,
            page=int(page),
            per_page=int(limit),
    )

    return {
        'code': 'ORG_API_SUCCESS',
        'data': [dict(zip(item.keys(), item)) for item in data.items],
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_org(org_id):
    """Update organization description and social.

    This API will have two situations.
    First: General user update the organization will check permission
    Second: Manager will update the organization directly
    """
    data = request.get_json()
    UpdateOrgSchema().load(data)

    org = check_org_exist(org_id)
    check_user_permission(org_id, True)

    description = data.get('description', None)
    if description:
        org.description = description

    social_params = data.get('social', None)
    if social_params:
        social = org.social if org.social_id else Social()
        social.update(social_params)
        g.db_session.add(social)

        if org.social_id is None:
            g.db_session.flush()
            org.social_id = social.id
    g.db_session.add(org)
    g.db_session.commit()

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>/leave', methods=['POST'])
@format_response
# @jwt_required
@check_jwt_user_exist
def leave_org(org_id):
    print('1----')
    check_org_exist(org_id)
    check_user_permission(org_id)

    subquery = g.db_session.query(Role) \
        .filter(Role.org_id == org_id) \
        .with_entities(Role.id).subquery()

    data = g.db_session.query(user_role) \
        .join(Role, Role.id == user_role.c.role_id) \
        .filter(Role.id.in_(subquery), user_role.c.user_id == g.current_user.id) \
        .with_entities(
            user_role.c.user_id,
            user_role.c.role_id,
            Role.org_id,
            Role.permission_id,
            Role.name
        ).first()

    g.db_session.execute(
        f"""
            UPDATE user_role
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE user_id = '70510b83-aaef-4ccd-8471-57296f6b14c2'
                AND role_id = '{data[1]}'
        """
    )

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>/invite', methods=['POST'])
@format_response
@jwt_required
@check_jwt_user_exist
def invite_member(org_id):
    """Invite member to organization.

    This API will have two situations.
    First: pass user_id
    Second: pass email, but if email have been used by a user.
        The API will invite the user who has this email.
    """
    # Step 1: Check parameters is valid
    data = request.get_json()
    InviteMemberSchema().load(data)

    # Step 2: Check organization is exist
    check_org_exist(org_id)

    # Step 3: Check user has permission to invite user to this organization
    check_user_permission(org_id, True)

    # Step 4: Check invitee user status
    # user_id: Check user exist
    # email: if email have been used then turn to user_id flow,
    #   rather than send email to sign up
    exist_member = None
    user_id = data.get('user_id', None)
    email = data.get('email', None)
    if user_id:
        exist_member = g.db_session.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).one_or_none()
        if exist_member is None:
            raise OrganizationException('member_not_exist')
    elif email:
        # The email in User table will be unique,
        #   so this won't check deleted_at
        email = email.lower()
        exist_member = g.db_session.query(User).filter_by(
            email=email
        ).one_or_none()

    # Step 5: Send email
    mail = SendGrid()
    if exist_member:
        req_log = RequestMemberLog(
            req_type='invite_exist_member',
            inviter_id=g.current_user.id,
            invitee_id=exist_member.id,
            org_id=org_id,
        )
        g.db_session.add(req_log)
        g.db_session.commit()
        mail.send(exist_member.email, 'INVITE_EXIST_MEMBER')
    elif email:
        req_log = RequestMemberLog(
            req_type='invite_member',
            inviter_id=g.current_user.id,
            email=email,
            org_id=org_id,
        )
        g.db_session.add(req_log)
        g.db_session.commit()
        mail.send(email, 'INVITE_MEMBER')
    else:
        raise OrganizationException()

    return {
        'code': 'USER_API_SUCCESS',
        'http_status_code': HTTPStatus.ACCEPTED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>/events', methods=['POST'])
@format_response
@jwt_required
@check_jwt_user_exist
def create_event(org_id):
    """Create event to organization with social and request log."""
    data = request.get_json()
    CreateEventSchema().load(data)

    check_org_exist(org_id)
    check_user_permission(org_id, True)

    event = Event(org_id=org_id)
    event_params = {}
    for (key, value) in data.items():
        if key in ('name', 'description'):
            event_params[key] = value
        elif '_at' in key:
            event_params[key] = datetime.utcfromtimestamp(int(value) * 1e-3)
    g.db_session.add(event)
    g.db_session.flush()

    social_params = data.get('social', None)
    if social_params:
        social = Social(**social_params)
        g.db_session.add(social)
        g.db_session.flush()
        event.social_id = social.id

    tickets = data.get('tickets', None)
    if tickets:
        for ticket in tickets:
            ticket_fare = TicketFare()
            ticket_fare.update(ticket)
            ticket_fare.event_id = event.id
            g.db_session.add(ticket_fare)

    if g.current_user_type == 'user':
        req_log = RequestEventLog(
            event_id=event.id,
            req_type='apply_event',
        )
        req_log.applicant_id = g.current_user.id
        g.db_session.add(req_log)

    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>/events', methods=['GET'])
@format_response
@jwt_required
@check_jwt_user_exist
def get_org_events(org_id):
    """Get organization's events for dashboard."""
    check_org_exist(org_id)
    check_user_permission(org_id)
    params = request.args.to_dict()
    page = params.get('page', 1)
    limit = params.get('limit', 20)

    subquery = g.db_session.query(RequestEventLog) \
        .order_by(RequestEventLog.created_at.desc()).subquery()

    data = g.db_session.query(Event) \
        .with_entities(
            Event.id,
            Event.name,
            Event.updated_at,
            subquery.c.approve_at
    ) \
        .filter(
            Event.deleted_at.is_(None),
            Event.org_id == org_id,
            subquery.c.deleted_at.is_(None)
    ) \
        .outerjoin(subquery, subquery.c.event_id == Event.id) \
        .order_by(Event.created_at.desc())  \
        .paginate(
            error_out=False,
            max_per_page=50,
            page=int(page),
            per_page=int(limit),
    )

    result = {
        'total': data.total,
        'pages': data.pages,
        'items': [dict(zip(item.keys(), item)) for item in data.items]
    }

    return {
        'code': 'EVENT_API_SUCCESS',
        'data': result,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>/events/<path:event_id>', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_event(org_id, event_id):
    """Update event with social."""
    data = request.get_json()
    UpdateEventSchema().load(data)

    check_org_exist(org_id)
    check_user_permission(org_id, True)
    event = check_event_exist(org_id, event_id)

    event_params = {}
    for (key, value) in data.items():
        if key not in ('social'):
            event_params[key] = value
    event.update(event_params)
    g.db_session.add(event)

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

    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>/events/<path:event_id>', methods=['DELETE'])
@format_response
@jwt_required
@check_jwt_user_exist
def delete_event(org_id, event_id):
    """Delete event."""
    check_org_exist(org_id)
    check_user_permission(org_id, True)
    event = check_event_exist(org_id, event_id)

    deleted_at = datetime.utcnow()
    event.deleted_at = deleted_at
    g.db_session.add(event)

    if event.social_id:
        event.social.deleted_at = deleted_at
        g.db_session.add(event.social)
    for req in event.requests:
        req.deleted_at = deleted_at
        g.db_session.add(req)
    for ticket in event.tickets:
        ticket.deleted_at = deleted_at
        g.db_session.add(ticket)

    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
