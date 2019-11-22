from datetime import datetime
from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import g, request
from marshmallow import Schema, ValidationError, fields, validate

from tsdip.formatter import format_response
from tsdip.models import Event, RequestLog, Social, Studio

api_blueprint = Blueprint('events', __name__, url_prefix='/events')


class SocialSchema(Schema):
    email = fields.Email()
    fan_page = fields.URL()
    instagram = fields.Str()
    line = fields.Str()
    telephone = fields.Str()
    website = fields.URL()
    youtube = fields.URL()


class CreateEventSchema(Schema):
    studio_id = fields.UUID(required=True)
    name = fields.Str(required=True)
    description = fields.Str()
    address = fields.Str()
    amount = fields.Int(required=True, validate=validate.Range(min=0))
    end_at = fields.TimeDelta(required=True)
    price = fields.Int(required=True, validate=validate.Range(min=0))
    reg_end_at = fields.TimeDelta(required=True)
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta(required=True)
    start_at = fields.TimeDelta(required=True)

    social = fields.Nested(SocialSchema)


@api_blueprint.route('/create', methods=['POST'])
@format_response
def create():
    """
    **summary** Create the event.

    **description**
    @api {post} /studios/create Create the event
    @apiName CreateEvent
    @apiGroup Event
    @apiDescription The API will create a event.
    It will create a request log that needs to wait for admin approve.

    @apiParam {UUID} studio_id
    @apiParam {String} name name need to be unique
    @apiParam {String} [description]
    @apiParam {DateTime} end_at
    @apiParam {DateTime} reg_end_at
    @apiParam {DateTime} reg_start_at
    @apiParam {DateTime} start_at
    @apiParam {Number} amount
    @apiParam {Number} price
    @apiParam {String} [address]
    @apiParam {URL} [reg_link]

    @apiParam {Email} [social.email]
    @apiParam {String} [social.fan_page]
    @apiParam {String} [social.instagram]
    @apiParam {String} [social.line]
    @apiParam {String} [social.telephone]
    @apiParam {URL} [social.website]
    @apiParam {URL} [social.youtube]
    """
    try:
        CreateEventSchema().load(request.get_json())
    except ValidationError as err:
        app.logger.error(err.messages)
        app.logger.error(err.valid_data)
        return {
            'code': 'ERROR_EVENT_1',
            'description': err.messages,
            'http_status_code': HTTPStatus.BAD_REQUEST,
            'status': 'ERROR',
        }

    data = request.get_json()
    studio_id = data['studio_id']

    try:
        studio = g.db_session.query(Studio).get(studio_id)
        if not studio or studio.deleted_at:
            return {
                'code': 'ERROR_EVENT_2',
                'http_status_code': HTTPStatus.BAD_REQUEST,
                'status': 'ERROR',
            }

        event = Event()
        social = Social()
        have_social = False

        for (key, value) in data.items():
            # event
            if key in ('name', 'description', 'amount', 'price', 'address',
                       'reg_link'):
                setattr(event, key, value)
            elif key in ('reg_start_at', 'reg_end_at', 'start_at', 'end_at'):
                convert_time = datetime.utcfromtimestamp(int(value) * 1e-3)
                setattr(event, key, convert_time)
            # social
            elif key == 'social':
                for (social_key, social_value) in value.items():
                    if social_key in ('email', 'fan_page', 'instagram', 'line',
                                      'telephone', 'website', 'youtube'):
                        have_social = True
                        setattr(social, social_key, social_value)

        if have_social:
            g.db_session.add(social)
            g.db_session.flush()
            event.social_id = social.id

        event.studio_id = studio_id
        g.db_session.add(event)
        g.db_session.flush()
        req_log = RequestLog(
            request='event',
            request_id=event.id
        )
        g.db_session.add(req_log)
        g.db_session.commit()
    except Exception as err:
        app.logger.error(err)
        g.db_session.rollback()

        return {
            'code': 'ERROR_EVENT_3',
            'description': str(err),
            'http_status_code': HTTPStatus.INTERNAL_SERVER_ERROR,
            'status': 'ERROR',
        }
    else:
        return {
            'code': 'ROUTE_EVENT_1',
            'http_status_code': HTTPStatus.CREATED,
            'status': 'SUCCESS',
        }
