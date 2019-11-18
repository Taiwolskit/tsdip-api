"""empty message

Revision ID: cbf42ed0c811
Revises:
Create Date: 2019-11-16 15:09:41.518088

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cbf42ed0c811'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('manager',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('telephone', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('telephone'),
    sa.UniqueConstraint('username')
    )
    op.create_table('social',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('fan_page', sa.String(length=255), nullable=True),
    sa.Column('instagram', sa.String(length=255), nullable=True),
    sa.Column('line', sa.String(length=255), nullable=True),
    sa.Column('telephone', sa.String(length=20), nullable=True),
    sa.Column('website', sa.String(length=255), nullable=True),
    sa.Column('youtube', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fan_page'),
    sa.UniqueConstraint('instagram'),
    sa.UniqueConstraint('line'),
    sa.UniqueConstraint('telephone'),
    sa.UniqueConstraint('website'),
    sa.UniqueConstraint('youtube')
    )
    op.create_table('event',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('amount', sa.Integer(), server_default='0', nullable=False),
    sa.Column('price', sa.Integer(), server_default='0', nullable=False),
    sa.Column('reg_link', sa.String(length=128), nullable=True),
    sa.Column('reg_start_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('reg_end_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('start_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('end_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('social_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.CheckConstraint('amount > -1'),
    sa.CheckConstraint('price > -1'),
    sa.ForeignKeyConstraint(['social_id'], ['social.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('reg_link')
    )
    op.create_table('request_log',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('request', postgresql.ENUM('event', 'invite', 'manager', 'studio', name='request_type'), server_default='event', nullable=False),
    sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('approve', sa.Boolean(), server_default='False', nullable=False),
    sa.Column('approve_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('approve_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['approve_by'], ['manager.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('studio',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('social_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['social_id'], ['social.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('permission',
    sa.Column('manager_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('studio_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('role', postgresql.ENUM('manager', 'owner', 'viewer', name='permission_role'), server_default='viewer', nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], ['manager.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['studio_id'], ['studio.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('manager_id', 'studio_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('permission')
    op.drop_table('studio')
    op.drop_table('request_log')
    op.drop_table('event')
    op.drop_table('social')
    op.drop_table('manager')
    # ### end Alembic commands ###
