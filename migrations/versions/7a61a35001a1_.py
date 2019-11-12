"""empty message

Revision ID: 7a61a35001a1
Revises: 
Create Date: 2019-11-12 11:11:43.252409

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7a61a35001a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coupon',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('code', sa.String(length=128), nullable=False),
    sa.Column('amount', sa.Integer(), server_default='1', nullable=False),
    sa.Column('start_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('end_at', postgresql.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('social',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('fan_page', sa.String(length=128), nullable=True),
    sa.Column('instagram', sa.String(length=128), nullable=True),
    sa.Column('line', sa.String(length=128), nullable=True),
    sa.Column('telephone', sa.String(length=128), nullable=True),
    sa.Column('website', sa.String(length=128), nullable=True),
    sa.Column('youtube', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('gender', postgresql.ENUM('secret', 'male', 'female', name='gen'), server_default='secret', nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.CheckConstraint('age > 7'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('dance_group',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('start_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('end_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('social_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['social_id'], ['social.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('event',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('amount', sa.Integer(), server_default='1', nullable=False),
    sa.Column('price', sa.Integer(), server_default='0', nullable=False),
    sa.Column('reg_link', sa.String(length=128), nullable=False),
    sa.Column('reg_start_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('reg_end_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('start_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('end_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('social_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['social_id'], ['social.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('reg_link')
    )
    op.create_table('studio',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('address', sa.String(length=128), nullable=False),
    sa.Column('social_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['social_id'], ['social.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('teachter',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('social_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['social_id'], ['social.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('course',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('start_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('end_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('substitute', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('studio_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('teachter_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['studio_id'], ['studio.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['teachter_id'], ['teachter.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('plan',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('price', sa.Integer(), server_default='0', nullable=False),
    sa.Column('point', sa.Integer(), server_default='0', nullable=False),
    sa.Column('start_at', postgresql.TIMESTAMP(), nullable=False),
    sa.Column('end_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('studio_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['studio_id'], ['studio.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rel_group_teachter',
    sa.Column('dance_group_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('teachter_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['dance_group_id'], ['dance_group.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['teachter_id'], ['teachter.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('dance_group_id', 'teachter_id')
    )
    op.create_table('rel_studio_teachter',
    sa.Column('studio_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('teachter_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['studio_id'], ['studio.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['teachter_id'], ['teachter.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('studio_id', 'teachter_id')
    )
    op.create_table('rel_lesson_log',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'course_id')
    )
    op.create_table('rel_purchase_log',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('coupon_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['coupon_id'], ['coupon.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'plan_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rel_purchase_log')
    op.drop_table('rel_lesson_log')
    op.drop_table('rel_studio_teachter')
    op.drop_table('rel_group_teachter')
    op.drop_table('plan')
    op.drop_table('course')
    op.drop_table('teachter')
    op.drop_table('studio')
    op.drop_table('event')
    op.drop_table('dance_group')
    op.drop_table('user')
    op.drop_table('social')
    op.drop_table('coupon')
    # ### end Alembic commands ###