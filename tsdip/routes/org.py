from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from tsdip.formatter import format_response
from tsdip.mail import SendGrid
from tsdip.models import (Organization, RequestMemberLog, RequestOrgLog,
                          Social, User)
from tsdip.schema.org import (CreateOrgSchema, InviteMemberSchema,
                              UpdateOrgSchema)

api_blueprint = Blueprint('organizations', __name__,
                          url_prefix='/organizations')


@api_blueprint.route('/create', methods=['POST'])
@format_response
@jwt_required
def create_org():
    """Create organization with social and request log."""
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

    req_log = RequestOrgLog(
        req_type='apply_org',
        org_id=org.id,
        applicant_id=current_user['id']
    )
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
def update_org(org_id):
    """Update organization with social."""
    data = request.get_json()
    UpdateOrgSchema().load(data)
    current_user = get_jwt_identity()
    current_user = g.db_session.query(User).get(current_user['id'])
    check_permission = False
    for role in current_user.roles:
        if role.name in ('owner', 'manager') and role.org_id == org_id:
            check_permission = True
            break
    if not check_permission:
        raise InviteMemberException('permission_denied')

    address = data.get('address', None)
    description = data.get('description', None)
    social_params = data.get('social', None)

    org = g.db_session.query(Organization).get(org_id)
    if address:
        org.address = address
    if description:
        org.description = description
    if social_params:
        for key, value in social_params.items():
            setattr(org.social, key, value)
    g.db_session.add(org)
    g.db_session.commit()

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


class InviteMemberException(Exception):
    """Invite member exception."""

    def __init__(self, comment="organization_miss"):
        """Exception constructor."""
        if comment == "organization_miss":
            self.message = "Organization is not exist"
        elif comment == 'permission_denied':
            self.message = "Permission denied, user is not have permission to do this action"
        elif comment == 'member_miss':
            self.message = 'Member is not exist'
        else:
            self.message = "Invite member exception comment empty"
        super().__init__(self.message)


@api_blueprint.route('/<path:org_id>/invite', methods=['POST'])
@format_response
@jwt_required
def invite_member(org_id):
    """Invite member to organization."""
    # Step 1: Check organization is exist
    org = g.db_session.query(Organization).get(org_id)
    if org is None or org.deleted_at:
        raise InviteMemberException('organization_miss')

    # Step 2: Check user has permission to invite user to this organization
    current_user = get_jwt_identity()
    current_user = g.db_session.query(User).get(current_user['id'])
    check_permission = False
    for role in current_user.roles:
        if role.permission.could_invite and role.org_id == org_id:
            check_permission = True
            break
    if not check_permission:
        raise InviteMemberException('permission_denied')

    data = request.get_json()
    InviteMemberSchema().load(data)

    # Step 3: Check invitee user status
    # user_id need to exist
    # If email have been used then turn to user_id flow, rather than
    # send email to sign up
    exist_member = None
    if 'user_id' in data:
        exist_member = g.db_session.query(User).get(data['user_id'])
        if exist_member is None or exist_member.deleted_at:
            raise InviteMemberException('member_miss')
    elif 'email' in data:
        exist_member = g.db_session.query(User).filter_by(
            email=data['email'].lower()
        ).one_or_none()

    # Step 4: Send email
    mail = SendGrid()
    if exist_member:
        req_log = RequestMemberLog(
            req_type='invite_exist_member',
            inviter_id=current_user.id,
            invitee_id=exist_member.id,
            org_id=org_id,
        )
        g.db_session.add(req_log)
        g.db_session.commit()
        mail.send(exist_member.email, 'INVITE_EXIST_MEMBER')
    elif 'email' in data:
        req_log = RequestMemberLog(
            req_type='invite_member',
            inviter_id=current_user.id,
            email=data['email'],
            org_id=org_id,
        )
        g.db_session.add(req_log)
        g.db_session.commit()
        mail.send(data['email'], 'INVITE_MEMBER')

    return {
        'code': 'USER_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
