from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy import or_

from tsdip.formatter import format_response
from tsdip.mail import SendGrid
from tsdip.models import Manager, RequestLog, Studio

api_blueprint = Blueprint('managers', __name__, url_prefix='/managers')


class ManagerSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    telephone = fields.Str()


@api_blueprint.route('/signup', methods=['POST'])
@format_response
def create():
    try:
        ManagerSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_MANAGER_1',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    data = request.get_json()
    email, username = data['email'], data['username']
    telephone = data['telephone'] if 'telephone' in data else None

    try:
        exist_manager = g.db_session.query(Manager).filter(
            or_(
                Manager.email == email,
                Manager.username == username
            )
        ).one_or_none()
        if exist_manager:
            raise Exception('Username or email had been used')

        manager = Manager(
            username=username,
            email=email,
            telephone=telephone
        )
        g.db_session.add(manager)
        g.db_session.flush()
        req_log = RequestLog(
            request='manager',
            request_id=manager.id
        )
        g.db_session.add(req_log)
        g.db_session.commit()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_MANAGER_2',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_MANAGER_1',
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }


@api_blueprint.route('/invite/<path:studio_id>', methods=['POST'])
@format_response
def invite(studio_id):
    try:
        ManagerSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_MANAGER_3',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    try:
        studio = g.db_session.query(Studio).get(studio_id)
        if not studio:
            raise Exception(f'Studio {studio_id} is not exist')
    except Exception as err:
        app.logger.error(err)
        return {
            'code': 'ERROR_MANAGER_3',
            'description': str(err),
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    mail = SendGrid()
    data = request.get_json()
    email, username = data['email'], data['username']
    telephone = data['telephone'] if 'telephone' in data else None

    try:
        exist_manager = g.db_session.query(Manager).filter(
            Manager.email == email,
            Manager.username == username
        ).one_or_none()

        if exist_manager:
            exist_manager.studios.append(studio)
        else:
            manager = Manager(
                email=email,
                telephone=telephone,
                username=username,
            )
            g.db_session.add(manager)
            g.db_session.flush()
            manager.studios.append(studio)

        g.db_session.commit()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_MANAGER_4',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        mail.send(email)
        return {
            'code': 'ROUTE_MANAGER_2',
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }


class ManagerUpdateSchema(Schema):
    username = fields.Str()
    email = fields.Email()
    telephone = fields.Str()


@api_blueprint.route('/<path:manager_id>', methods=['PUT'])
@format_response
def update(manager_id):
    try:
        ManagerUpdateSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_MANAGER_5',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    try:
        manager = g.db_session.query(Manager).get(manager_id)
        if not manager:
            raise Exception(f'Manager {manager_id} is not exist')
    except Exception as err:
        app.logger.error(err)
        return {
            'code': 'ERROR_MANAGER_5',
            'description': str(err),
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    data = request.get_json()

    try:
        for (key, value) in data.items():
            setattr(manager, key, value)

        g.db_session.add(manager)
        g.db_session.commit()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_MANAGER_6',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_MANAGER_3',
            'http_status_code': HTTPStatus.ACCEPTED,
            'status': 'SUCCESS',
        }


class ManagerPermissionSchema(Schema):
    studio_id = fields.UUID(required=True)
    role = fields.Str(
        required=True,
        validate=validate.OneOf(["viewer", "manager", "owner", "break"])
    )


@api_blueprint.route('/permission/<path:manager_id>', methods=['PUT'])
@format_response
def update_permission(manager_id):
    """
    @TODO check user permission
    """
    try:
        ManagerPermissionSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_MANAGER_7',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    data = request.get_json()
    role, studio_id = data['role'], data['studio_id']

    try:
        manager = g.db_session.query(Manager).get(manager_id)
        if not manager:
            raise Exception(f'Manager {manager_id} is not exist')

        studio = g.db_session.query(Studio).get(studio_id)
        if not studio:
            raise Exception(f'Studio {studio_id} is not exist')
    except Exception as err:
        app.logger.error(err)
        return {
            'code': 'ERROR_MANAGER_7',
            'description': str(err),
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    try:
        if role == 'break':
            manager.studios.remove(studio)
        else:
            g.db_session.execute(
                """
                UPDATE permission
                SET role = :role
                WHERE manager_id = :manager_id
                    AND studio_id = :studio_id
                """,
                {
                    'role': role,
                    'manager_id': manager_id,
                    'studio_id': studio_id
                }
            )
        g.db_session.commit()
    except Exception as err:
        app.logger.error(err)
        return {
            'code': 'ERROR_MANAGER_8',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_MANAGER_4',
            'http_status_code': HTTPStatus.OK,
            'status': 'SUCCESS',
        }
