from http import HTTPStatus

from flask import Blueprint, g

from tsdip.formatter import format_response
from tsdip.models import Event, MyStuff

api_blueprint = Blueprint('events', __name__, url_prefix='/events')


class EventException(Exception):
    """Event exception."""

    def __init__(self, comment):
        """Exception constructor."""
        if comment == "event_not_exist":
            self.message = "Event is not exist"
        else:
            self.message = "Create event exception comment empty"
        super().__init__(self.message)


@api_blueprint.route('/<path:event_id>', methods=['GET'])
@format_response
def get_single_event(event_id):
    print('1-------')
    """Get single event detail with social."""
    # event = g.db_session.query(Event).filter(
    #     Event.id == event_id,
    #     Event.deleted_at.is_(None)
    # ).one_or_none()
    # if event is None:
    #     raise EventException('event_not_exist')

    # result = event.as_dict(filter_at=True)
    # if event.social:
    #     result['social'] = event.social.event.as_dict(filter_at=True)

    cc = g.db_session.query(MyStuff).filter(
        MyStuff.id == '3f4d03a5-c40d-4e8e-83c9-a9a9afaedf42'
    ).one_or_none()
    print(cc)
    # for row in cc:
    #     print(row.id)

    return {
        'code': 'EVENT_API_SUCCESS',
        'data': 'result',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }
