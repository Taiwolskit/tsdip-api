from http import HTTPStatus

from flask import Blueprint, g, request

from flask_jwt_extended import get_jwt_identity, jwt_required
from tsdip.formatter import format_response
from tsdip.models import Organization, RequestOrgLog, Social
from tsdip.schema.org import CreateOrgSchema

api_blueprint = Blueprint('organizations', __name__, url_prefix='/organizations')


@api_blueprint.route('/create', methods=['POST'])
@format_response
@jwt_required
def create_org():
    """Create organization with social and request log."""
    data = request.get_json()
    CreateOrgSchema().load(data)
    current_user = get_jwt_identity['id']
    name = data['name']
    org_type = data['org_type']

    description = data.get('description', None)
    address = data.get('address', None)
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
