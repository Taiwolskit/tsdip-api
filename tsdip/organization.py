from flask import g

from tsdip.models import Organization, RequestOrgLog, VWUserPermission


def get_user_organizations(user_id, page=1, limit=20, org_type=None):
    subquery = g.db_session.query(VWUserPermission) \
        .filter_by(user_id=user_id) \
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
    return result


def get_user_reviewing_organizations(user_id, page=1, limit=20, org_type=None):
    subquery = g.db_session.query(RequestOrgLog) \
        .filter(
            RequestOrgLog.applicant_id == user_id,
            RequestOrgLog.approve_at.is_(None),
            RequestOrgLog.deleted_at.is_(None)
    ) \
        .outerjoin(Organization, RequestOrgLog.org_id == Organization.id) \
        .filter(
            Organization.deleted_at.is_(None)
    ) \
        .with_entities(
            Organization.id,
            Organization.name,
            Organization.org_type,
            RequestOrgLog.req_type,
            RequestOrgLog.applicant_id,
    )

    if org_type:
        subquery = subquery.filter(Organization.org_type == org_type)

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
        'items': [dict(zip(org.keys(), org)) for org in data.items]
    }
    return result
