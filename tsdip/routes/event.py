from http import HTTPStatus

from flask import Blueprint, g, request

from tsdip.formatter import format_response
from tsdip.models import Event, VWOrgApproveStatus, RequestEventLog

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

    cc = g.db_session.query(VWOrgApproveStatus).filter(
        VWOrgApproveStatus.org_id == '08ac9b31-6e41-496e-9794-ce2c45a325f5'
    ).one_or_none()
    print(cc.org_id)
    print(cc.org_type)
    # for row in cc:
    #     print(row)

    return {
        'code': 'EVENT_API_SUCCESS',
        'data': 'result',
        'http_status_code': HTTPStatus.OK,
        'status': 'SUCCESS',
    }


@api_blueprint.route('/', methods=['GET'])
@format_response
def get_events():
    params = request.args.to_dict()
    query_type = params.get('query_type', 'latest')

    if query_type == 'latest':
        subquery = g.db_session.query(RequestEventLog).filter(
            RequestEventLog.approve_at.isnot(None))
        data = g.db_session.query(Event).outerjoin(RequestEventLog, subquery.c.event_id == Event.id) \
            .order_by(subquery.c.approve_at.desc()).paginate(
            page=1,
            per_page=20,
            error_out=False,
            max_per_page=20
        )
    elif query_type == 'popular':
        pass
    pass
