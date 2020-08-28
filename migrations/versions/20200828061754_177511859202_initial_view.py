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


vw_demo = ReplaceableObject(
    "vw_demo",
    """
    SELECT
        public.user.id
    FROM
        public.user
        LEFT JOIN public.user_role ON public.user_role.user_id = public.user.id
    """
)


def upgrade():
    op.create_view(vw_demo)


def downgrade():
    op.drop_view(vw_demo)
