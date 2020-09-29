"""Initialize view

Revision ID: 177511859202
Revises: 8b54bb3fc4c5
Create Date: 2020-08-28 06:17:54.471238

"""
from alembic import op
from tsdip.view import ReplaceableObject

# revision identifiers, used by Alembic.
revision = '177511859202'
down_revision = '8b54bb3fc4c5'
branch_labels = None
depends_on = None


vw_org_approve_status = ReplaceableObject(
    "vw_org_approve_status",
    """
        SELECT
            org.id AS org_id,
            org.name AS org_name,
            org.org_type,
            org.approve_at AS org_approve_at,
            rol.req_type,
            rol.approve_at,
            rol.applicant_id,
            rol.approver_id
        FROM
            organization AS org
            LEFT JOIN request_org_log AS rol ON rol.org_id = org.id
        WHERE
            org.deleted_at IS NULL
            AND rol.deleted_at IS NULL
    """
)


vw_event_approve_status = ReplaceableObject(
    "vw_event_approve_status",
    """
        SELECT
            event.id AS event_id,
            event.name AS event_name,
            event.published_at,
            event.approve_at AS event_approve_at,
            rol.req_type,
            rol.approve_at,
            rol.applicant_id,
            rol.approver_id
        FROM
            event
            LEFT JOIN request_event_log AS rol ON rol.event_id = event.id
        WHERE
            event.deleted_at IS NULL
            AND rol.deleted_at IS NULL
    """
)


vw_user_permission = ReplaceableObject(
    "vw_user_permission",
    """
        SELECT
            temp.user_id,
            temp.role_id,
            temp.role,
            p.id AS permission_id,
            org.id AS org_id,
            org.org_type
        FROM
            (
                (
                    SELECT
                        r.id AS role_id,
                        u.id AS user_id,
                        r.permission_id,
                        r.org_id,
                        r.name AS role
                    FROM
                        (
                            user_role AS ur
                            LEFT JOIN "user" AS u ON u.id = ur.user_id
                        )
                        LEFT JOIN role r ON r.id = ur.role_id
                    WHERE
                        u.deleted_at IS NULL
                        AND ur.deleted_at IS NULL
                        AND r.deleted_at IS NULL
                ) temp
                LEFT JOIN permission AS p ON temp.permission_id = p.id
            )
            LEFT JOIN organization AS org ON temp.org_id =org.id
        WHERE
            p.deleted_at IS NULL
            AND org.deleted_at IS NULL
    """
)


def upgrade():
    op.create_view(vw_org_approve_status)
    op.create_view(vw_event_approve_status)
    op.create_view(vw_user_permission)


def downgrade():
    op.drop_view(vw_org_approve_status)
    op.drop_view(vw_event_approve_status)
    op.drop_view(vw_user_permission)
