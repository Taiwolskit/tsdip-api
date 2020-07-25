from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from tsdip.auth import check_jwt_user_exist
from tsdip.formatter import format_response
from tsdip.mail import SendGrid
from tsdip.models import (Event, Organization, RequestEventLog,
                          RequestMemberLog, RequestOrgLog, Social, User)
from tsdip.schema.org import (CreateEventSchema, CreateOrgSchema,
                              InviteMemberSchema, UpdateEventSchema,
                              UpdateOrgSchema)

api_blueprint = Blueprint('organizations', __name__,
                          url_prefix='/organizations')


class OrganizationException(Exception):
    """Invite member exception."""

    def __init__(self, comment):
        """Exception constructor."""
        if comment == "organization_not_exist":
            self.message = "Organization is not exist"
        elif comment == 'permission_denied':
            self.message = "Permission denied, user does not have permission to do this action"
        elif comment == 'member_not_exist':
            self.message = 'Member is not exist'
        else:
            self.message = "Organization exception comment empty"
        super().__init__(self.message)


def check_org_exist(org_id):
    """Check organization exist or not."""
    org = g.db_session.query(Organization).filter(
        Organization.id == org_id,
        Organization.deleted_at.isnot(None)
    ).one_or_none()
    if org is None:
        raise OrganizationException('organization_not_exist')
    return org


def check_event_exist(org_id, event_id):
    """Check event exist or not."""
    event = g.db_session.query(Event).filter(
        Event.id == event_id,
        Event.org_id == org_id,
        Event.deleted_at.isnot(None)
    ).one_or_none()
    if event is None:
        raise EventException('event_not_exist')
    return event


def check_user_permission(current_user, org):
    """Check user permission for the organization."""
    if current_user['type'] != 'manager' and org.claim_at is not None:
        check_permission = False
        for role in g.current_user.roles:
            if role.org_id == org.org_id:
                check_permission = True
                break
        if check_permission is False:
            raise OrganizationException('permission_denied')


@api_blueprint.route('/create', methods=['POST'])
@format_response
@jwt_required
@check_jwt_user_exist
def create_org():
    """Create organization with social and request log.

    This API will have two situations.
    First: General user create the organization
    Second: Manager create the organization,
        the applicant_id of request log will be empty
    """
    data = request.get_json()
    CreateOrgSchema().load(data)
    current_user = get_jwt_identity()

    name = data.get('name')
    org_type = data.get('org_type')
    address = data.get('address', None)
    description = data.get('description', None)
    social_params = data.get('social', None)

    org = Organization(
        address=address,
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

    if current_user['type'] != 'manager':
        req_log = RequestOrgLog(
            req_type='apply_org',
            org_id=org.id
        )
        req_log.applicant_id = current_user['id']
        g.db_session.add(req_log)

    g.db_session.commit()

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_org(org_id):
    """Update organization with social.

    This API will have two situations.
    First: General user update the organization
    Second: Manager update the organization,
        but it could only update dereliction
    """
    data = request.get_json()
    UpdateOrgSchema().load(data)

    org = check_org_exist(org_id)
    current_user = get_jwt_identity()
    check_user_permission(current_user, org)

    address = data.get('address', None)
    description = data.get('description', None)
    social_params = data.get('social', None)
    if address:
        org.address = address
    if description:
        org.description = description
    if social_params and org.social:
        for key, value in social_params.items():
            setattr(org.social, key, value)
    g.db_session.add(org)
    g.db_session.commit()

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
    org = check_org_exist(org_id)

    # Step 3: Check user has permission to invite user to this organization
    current_user = get_jwt_identity()
    check_user_permission(current_user.roles, org)

    # Step 4: Check invitee user status
    # user_id: Check user exist
    # email: if email have been used then turn to user_id flow,
    #   rather than send email to sign up
    exist_member = None
    user_id = data.get('user_id', None)
    email = data.get('email', None)
    if user_id is None:
        exist_member = g.db_session.query(User).filter(
            User.id == user_id,
            User.deleted_at.isnot(None)
        ).one_or_none()
        if exist_member is None:
            raise OrganizationException('member_not_exist')
    elif email is None:
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
            inviter_id=current_user['id'],
            invitee_id=exist_member.id,
            org_id=org_id,
        )
        g.db_session.add(req_log)
        g.db_session.commit()
        mail.send(exist_member.email, 'INVITE_EXIST_MEMBER')
    elif email is not None:
        req_log = RequestMemberLog(
            req_type='invite_member',
            inviter_id=current_user['id'],
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
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


class EventException(Exception):
    """Event exception."""

    def __init__(self, comment="permission_denied"):
        """Exception constructor."""
        if comment == "event_not_exist":
            self.message = "Event is not exist"
        else:
            self.message = "Event exception comment empty"
        super().__init__(self.message)


@api_blueprint.route('/<path:org_id>/events', methods=['POST'])
@format_response
@jwt_required
@check_jwt_user_exist
def create_event(org_id):
    """Create event to organization with social and request log."""
    data = request.get_json()
    CreateEventSchema().load(data)

    org = check_org_exist(org_id)
    current_user = get_jwt_identity()
    check_user_permission(current_user, org)

    event = Event(org_id=org_id)
    for (key, value) in data.items():
        if key in ('name', 'description', 'amount', 'price', 'address', 'reg_link'):
            setattr(event, key, value)
        elif key in ('reg_start_at', 'reg_end_at', 'start_at', 'end_at'):
            convert_time = datetime.utcfromtimestamp(int(value) * 1e-3)
            setattr(event, key, convert_time)
    g.db_session.add(event)
    g.db_session.flush()

    social_params = data.get('social', None)
    if social_params:
        social = Social(**social_params)
        g.db_session.add(social)
        g.db_session.flush()
        event.social_id = social.id

    req_log = RequestEventLog(
        event_id=event.id,
        req_type='apply_event',
    )
    if current_user['type'] != 'manager':
        req_log.applicant_id = current_user['id']

    g.db_session.add(req_log)
    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
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

    org = check_org_exist(org_id)
    event = check_event_exist(org_id, event_id)

    current_user = get_jwt_identity()
    check_user_permission(current_user, org)

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


@api_blueprint.route('/<path:org_id>/events/<path:event_id>', methods=['DELETE'])
@format_response
@jwt_required
@check_jwt_user_exist
def delete_event(org_id, event_id):
    """Delete event."""
    org = check_org_exist(org_id)
    event = check_event_exist(org_id, event_id)

    current_user = get_jwt_identity()
    check_user_permission(current_user, org)

    event.deleted_at = datetime.utcnow()
    event.social.deleted_at = datetime.utcnow()
    for req in event.requests:
        req.deleted_at = datetime.utcnow()

    g.db_session.add(event)
    g.db_session.commit()

    return {
        'code': 'EVENT_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
