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


def upgrade():
    op.create_view(vw_org_approve_status)


def downgrade():
    op.drop_view(vw_org_approve_status)
