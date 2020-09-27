from http import HTTPStatus

from flask import Blueprint, g, request
from sqlalchemy import or_

from tsdip.auth import validate_api_token
from tsdip.formatter import format_response
from tsdip.models import Manager
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


# @api_blueprint.route('', methods=['GET'], strict_slashes=False)
# @format_response
# # @jwt_required
# @check_jwt_user_exist
# def get_orgs():
#     """Get organization list.

#     This API only provider for managers
#     """
#     params = request.args.to_dict()
#     page = params.get('page', 1)
#     limit = params.get('limit', 20)

#     if g.current_user_type != 'manager':
#         raise OrganizationException('permission_denied')

#     data = g.db_session.query(Organization).filter(
#         Organization.deleted_at.is_(None)
#     ).order_by(Organization.created_at.desc())  \
#         .paginate(
#             error_out=False,
#             max_per_page=50,
#             page=int(page),
#             per_page=int(limit),
#     )

#     return {
#         'code': 'ORG_API_SUCCESS',
#         'data': [dict(zip(item.keys(), item)) for item in data.items],
#         'http_status_code': HTTPStatus.CREATED,
#         'status': 'SUCCESS',
#     }
