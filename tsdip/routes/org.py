from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, g, request
from flask_jwt_extended import jwt_optional, jwt_required
from tsdip.auth import check_jwt_user_exist
from tsdip.formatter import format_response
from tsdip.models import (Event, Organization, RequestEventLog, RequestOrgLog,
                          Social, TicketFare, VWOrgApproveStatus,
                          VWUserPermission)
from tsdip.schema.org import (CreateEventSchema, CreateOrgSchema,
                              GetOrgsSchema, SocialSchema, UpdateOrgSchema)

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


def check_org_approve(org_id):
    """Check organization had been approve or not."""
    # First: Check organization has been approve or not.
    req_log = g.db_session.query(VWOrgApproveStatus).filter(
        VWOrgApproveStatus.org_id == org_id,
        VWOrgApproveStatus.req_type.in_(['apply_org', 'claim_org']),
    ).one_or_none()

    # Second: Check organization have approve_at or not
    if req_log is None:
        org = check_org_exist(org_id)
        if org.approve_at is None:
            raise OrganizationException('organization_not_approve')
        return org
    else:
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


@api_blueprint.route('', methods=['POST'], strict_slashes=False)
@format_response
@jwt_required
@check_jwt_user_exist
def create_organization():
    """Create organization with social and request log.

    This API has two situations.
    First: General user create the organization, it create request log.
        The user permission create until the request has been approved.
    Second: Manager create the organization,
        it won't create request log but set approved at.
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
    elif g.current_user_type == 'manager':
        org.approve_at = datetime.utcnow()

    g.db_session.commit()

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }


@api_blueprint.route('', methods=['GET'], strict_slashes=False)
@format_response
@jwt_optional
@check_jwt_user_exist
def get_organizations():
    """Get organizations.

    This API has three situations.
    1. For public, query the org which is not deleted and has been approved.
    2. For organization users, query the org which the user has permission.
    3. For admin, query all organizations which are not deleted.
    """
    params = request.args.to_dict()
    GetOrgsSchema().load(params)
    page = params.get('page', 1)
    limit = params.get('limit', 20)
    org_type = params.get('org_type', None)

    result = None
    subquery = None
    if g.current_user is None:  # Public
        subquery = g.db_session.query(Organization).filter(
            Organization.deleted_at.is_(None),
            Organization.approve_at.isnot(None)
        )
        if org_type:
            subquery = subquery.filter_by(org_type=org_type)

        data = subquery.order_by(Organization.name.desc())  \
            .paginate(
                error_out=False,
                max_per_page=50,
                page=int(page),
                per_page=int(limit),
        )
        result = {
            'total': data.total,
            'pages': data.pages,
            'items': [org.to_public() for org in data.items]
        }
    elif g.current_user_type == 'user':  # For organization users
        subquery = g.db_session.query(VWUserPermission) \
            .filter_by(user_id=g.current_user.id) \
            .outerjoin(Organization, VWUserPermission.org_id == Organization.id)
        if org_type:
            subquery = subquery.filter_by(org_type=org_type)

        data = subquery.order_by(Organization.name.desc())  \
            .paginate(
                error_out=False,
                max_per_page=50,
                page=int(page),
                per_page=int(limit),
        )
        result = {
            'total': data.total,
            'pages': data.pages,
            'items': [org.as_dict() for org in data.items]
        }
    elif g.current_user_type == 'manager':  # For admin
        subquery = g.db_session.query(Organization).filter(
            Organization.deleted_at.is_(None)
        )
        if org_type:
            subquery = subquery.filter_by(org_type=org_type)

        data = subquery.order_by(Organization.name.desc())  \
            .paginate(
                error_out=False,
                max_per_page=50,
                page=int(page),
                per_page=int(limit),
        )
        result = {
            'total': data.total,
            'pages': data.pages,
            'items': [org.as_dict() for org in data.items]
        }

    return {
        'code': 'ORG_API_SUCCESS',
        'data': result,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>', methods=['GET'])
@format_response
@jwt_optional
@check_jwt_user_exist
def get_single_organization(org_id):
    """Get single organization.

    This API has three situations.
    1. For public, query the org which is not deleted and has been approved.
    2. For organization users, query the org which the user has permission.
    3. For admin, query all organizations which are not deleted.
    """
    org = check_org_exist(org_id)

    result = None
    if g.current_user is None:  # Public
        check_org_approve(org_id)
        result = org.to_public()
        if org.social_id:
            result['social'] = org.social.as_dict()
    elif g.current_user_type == 'user':  # For organization mangagers
        check_user_permission(org_id)
        result = org.as_dict()
        if org.social_id:
            result['social'] = org.social.as_dict()
    elif g.current_user_type == 'manager':  # For admin
        result = org.as_dict()
        if org.social_id:
            result['social'] = org.social.as_dict()

    return {
        'code': 'ORG_API_SUCCESS',
        'data': result,
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_organization(org_id):
    """Update organization description."""
    data = request.get_json()
    UpdateOrgSchema().load(data)

    org = check_org_exist(org_id)
    check_user_permission(org_id, True)

    description = data.get('description', None)
    if description:
        org.description = description

    g.db_session.add(org)
    g.db_session.commit()

    return {
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/<path:org_id>/social', methods=['PUT'])
@format_response
@jwt_required
@check_jwt_user_exist
def update_organization_socail(org_id):
    """Update organization's social."""
    data = request.get_json()
    SocialSchema().load(data)

    org = check_org_exist(org_id)
    check_user_permission(org_id, True)

    social = org.social if org.social_id else Social()
    social.update(data)
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


@api_blueprint.route('/<path:org_id>/events', methods=['POST'])
@format_response
@jwt_required
@check_jwt_user_exist
def create_organization_event(org_id):
    """Create event of organization with social, tickets and request log.

    This API will have two situations.
    First: General user create the data which is include request log
    Second: Manager create the data which is not include request log
    """
    data = request.get_json()
    CreateEventSchema().load(data)
    check_org_exist(org_id)
    check_user_permission(org_id, True)

    event = Event(
        name=data['name'],
        org_id=org_id
    )
    event_params = {}
    for (key, value) in data.items():
        if key == 'description':
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
            ticket_fare = TicketFare(name=ticket['name'])
            ticket_fare.update(ticket)
            ticket_fare.event_id = event.id
            if g.current_user_type == 'user':
                ticket_fare.creator_id = g.current_user.id
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
        'code': 'ORG_API_SUCCESS',
        'http_status_code': HTTPStatus.CREATED,
        'status': 'SUCCESS',
    }
