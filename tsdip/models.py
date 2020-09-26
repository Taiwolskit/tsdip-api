from datetime import datetime

from sqlalchemy import CheckConstraint, func, join, select, text
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.sql import expression

from tsdip import db, metadata
from tsdip.view import view

MANAGER_FOREKEY_FIELD = 'manager.id'
ORG_FOREKEY_FIELD = 'organization.id'
USER_FOREKEY_FIELD = 'user.id'

ViewBase = declarative_base(metadata=metadata)


class Base():
    """ORM model base structure."""

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('uuid_generate_v4()')
    )
    created_at = db.Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp()
    )
    updated_at = db.Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp()
    )
    deleted_at = db.Column(TIMESTAMP)

    def update(self, params):
        """ORM model base update function."""
        for key, value in params.items():
            if '_at' in key:
                convert_time = datetime.utcfromtimestamp(int(value) * 1e-3)
                setattr(self, key, convert_time)
            else:
                setattr(self, key, value)

    def as_dict(self, filter_at=False):
        """ORM model base convert object to dict function."""
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if filter_at:
            del temp['id']
            del temp['created_at']
            del temp['updated_at']
            del temp['deleted_at']

        return temp


class Social(db.Model, Base):
    """ORM Social model."""

    address = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    fan_page = db.Column(db.String(255), unique=True)
    instagram = db.Column(db.String(255), unique=True)
    line = db.Column(db.String(255), unique=True)
    telephone = db.Column(db.String(20), unique=True)
    website = db.Column(db.String(255), unique=True)
    youtube = db.Column(db.String(255), unique=True)

    @validates('address', 'email', 'fan_page', 'instagram', 'line', 'telephone', 'website', 'youtube')
    def convert_lower(self, key, value):
        """Convert field to lower case."""
        return value.lower()


class Event(db.Model, Base):
    """ORM Event model."""

    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    start_at = db.Column(TIMESTAMP)
    end_at = db.Column(TIMESTAMP)
    reg_link = db.Column(db.String(128))
    reg_start_at = db.Column(TIMESTAMP)
    reg_end_at = db.Column(TIMESTAMP)

    approved_at = db.Column(TIMESTAMP)
    published_at = db.Column(TIMESTAMP)

    creator_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    approver_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(MANAGER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    org_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(ORG_FOREKEY_FIELD, onupdate='CASCADE',
                      ondelete='SET NULL'),
        nullable=False
    )
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='SET NULL')
    )

    approver = db.relationship('Manager', uselist=False)
    creator = db.relationship('User', uselist=False)
    org = db.relationship('Organization', uselist=False)
    requests = db.relationship('RequestEventLog', lazy=True)
    social = db.relationship('Social', uselist=False)
    tickets = db.relationship('TicketFare', lazy=True)


class TicketFare(db.Model, Base):
    """ORM Ticket Fare model."""

    __table_args__ = (
        CheckConstraint('amount > -1'),
        CheckConstraint('price > -1'),
    )

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Integer, nullable=False, server_default='0')
    price = db.Column(db.Integer, nullable=False, server_default='0')
    reg_link = db.Column(db.String(128))
    reg_start_at = db.Column(TIMESTAMP)
    reg_end_at = db.Column(TIMESTAMP)

    creator_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    event_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('event.id', onupdate='CASCADE', ondelete='SET NULL')
    )

    creator = db.relationship('User', uselist=False)
    event = db.relationship('Event', uselist=False)


class Organization(db.Model, Base):
    """ORM Organization model."""

    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    org_type = db.Column(
        ENUM('dance_group', 'studio', name='org_type'),
        nullable=False,
        server_default='studio'
    )

    approved_at = db.Column(TIMESTAMP)
    published_at = db.Column(TIMESTAMP)

    creator_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    approver_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(MANAGER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='SET NULL')
    )

    approver = db.relationship('Manager', uselist=False)
    creator = db.relationship('User', uselist=False)
    events = db.relationship('Event', lazy=True)
    requests = db.relationship('RequestOrgLog', lazy=True)
    social = db.relationship('Social', uselist=False)


class Permission(db.Model, Base):
    """ORM Permission model."""

    manage_member = db.Column(db.Boolean, nullable=False,
                              server_default=expression.false())


class Role(db.Model, Base):
    """ORM Role model."""

    __table_args__ = (
        db.UniqueConstraint('org_id', 'permission_id',
                            name='uq_role_org_id_permission_id'),
    )

    name = db.Column(
        ENUM('owner', 'manager', 'viewer', name='role_name'),
        nullable=False,
        server_default='viewer'
    )
    org_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(ORG_FOREKEY_FIELD, onupdate='CASCADE',
                      ondelete='SET NULL'),
        nullable=False
    )
    permission_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('permission.id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=False
    )

    org = db.relationship('Organization', uselist=False)
    permission = db.relationship('Permission', uselist=False)


user_role = db.Table(
    'user_role',
    db.metadata,
    db.Column(
        'user_id',
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD, onupdate='CASCADE',
                      ondelete='SET NULL'),
        primary_key=True
    ),
    db.Column(
        'role_id',
        UUID(as_uuid=True),
        db.ForeignKey('role.id', onupdate='CASCADE', ondelete='SET NULL'),
        primary_key=True
    ),
    db.Column(
        'created_at',
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp()
    ),
    db.Column(
        'updated_at',
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp()
    ),
    db.Column(
        'deleted_at',
        TIMESTAMP
    )
)


class User(db.Model, Base):
    """ORM User model."""

    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(20), unique=True)

    roles = db.relationship('Role', secondary=user_role, lazy='dynamic')
    org_requests = db.relationship('RequestOrgLog', lazy=True)
    event_requests = db.relationship('RequestEventLog', lazy=True)
    invite_requests = db.relationship(
        'RequestMemberLog', lazy=True, foreign_keys='RequestMemberLog.inviter_id')
    invitee_requests = db.relationship(
        'RequestMemberLog', lazy=True, foreign_keys='RequestMemberLog.invitee_id')

    @validates('email', 'username')
    def convert_lower(self, key, value):
        """Convert field to lower case."""
        return value.lower()


class RequestOrgLog(db.Model, Base):
    """ORM RequestOrgLog model."""

    req_type = db.Column(
        ENUM('apply_org', 'claim_org', name='req_org_type'),
        nullable=False,
        server_default='apply_org'
    )
    org_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(ORG_FOREKEY_FIELD, onupdate='CASCADE',
                      ondelete='SET NULL'),
        nullable=False
    )
    applicant_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL'),
        nullable=False
    )
    approver_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(MANAGER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    approve_at = db.Column(TIMESTAMP)

    applicant = db.relationship('User', uselist=False)
    approver = db.relationship('Manager', uselist=False)
    org = db.relationship('Organization', uselist=False)


class RequestEventLog(db.Model, Base):
    """ORM RequestEventLog model."""

    req_type = db.Column(
        ENUM('apply_event', 'publish_event',
             'unpublish_event', name='req_event_type'),
        nullable=False,
        server_default='apply_event'
    )
    event_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('event.id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=False
    )
    applicant_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL'),
        nullable=False
    )
    approver_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(MANAGER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    approve_at = db.Column(TIMESTAMP)

    applicant = db.relationship('User', uselist=False)
    approver = db.relationship('Manager', uselist=False)
    event = db.relationship('Event', uselist=False)


class RequestMemberLog(db.Model, Base):
    """ORM RequestMemberLog model."""

    req_type = db.Column(
        ENUM('invite_member', 'invite_exist_member',
             'remove_member', name='req_member_type'),
        nullable=False,
        server_default='invite_member'
    )
    email = db.Column(db.String(255))
    org_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(ORG_FOREKEY_FIELD, onupdate='CASCADE',
                      ondelete='SET NULL'),
        nullable=False
    )
    inviter_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL'),
        nullable=False
    )
    invitee_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='SET NULL')
    )
    accepted_at = db.Column(TIMESTAMP)

    org = db.relationship('Organization', uselist=False)
    inviter = db.relationship('User', uselist=False, foreign_keys=inviter_id)
    invitee = db.relationship('User', uselist=False, foreign_keys=invitee_id)

    @validates('email')
    def convert_lower(self, key, value):
        """Convert field to lower case."""
        return value.lower()


class Manager(db.Model, Base):
    """ORM Manager model."""

    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(20), unique=True)

    @validates('email', 'username')
    def convert_lower(self, key, value):
        """Convert field to lower case."""
        return value.lower()


class VWOrgApproveStatus(ViewBase):
    """View: Organization approve status."""

    view_logic = select(
        [
            Organization.id.label('org_id'),
            Organization.name.label('org_name'),
            Organization.org_type.label('org_type'),
            RequestOrgLog.req_type.label('req_type'),
            RequestOrgLog.approve_at.label('approve_at'),
            RequestOrgLog.applicant_id.label('applicant_id'),
            RequestOrgLog.approver_id.label('approver_id'),
        ],
        use_labels=True
    ).select_from(
        join(
            RequestOrgLog,
            Organization,
            RequestOrgLog.org_id == Organization.id
        )
    ) \
        .where(Organization.deleted_at.is_(None)) \
        .where(RequestOrgLog.deleted_at.is_(None))

    __table__ = view("vw_org_approve_status", metadata, view_logic)


class VWUserPermission(ViewBase):
    """View: User permission relation."""

    first_logic = select(
        [
            User.id.label('user_id'),
            Role.id.label('role_id'),
            Role.permission_id.label('permission_id'),
            Role.org_id.label('org_id'),
            Role.name.label('role'),
        ],
        use_labels=True
    ).select_from(
        join(User, user_role, User.id == user_role.c.user_id)
        .join(Role, user_role, Role.id == user_role.c.role_id)
    ) \
        .where(User.deleted_at.is_(None)) \
        .where(user_role.c.deleted_at.is_(None)) \
        .where(Role.deleted_at.is_(None))

    view_logic = select(
        [
            first_logic.c.user_id,
            first_logic.c.role_id,
            first_logic.c.role,
            Permission.id.label('permission_id'),
            Organization.id.label('org_id'),
            Organization.org_type.label('org_type')
        ],
        use_labels=True
    ).select_from(
        join(Permission, first_logic, Permission.id ==
             first_logic.c.permission_id)
        .join(Organization, first_logic, Organization.id == first_logic.c.org_id)
    ) \
        .where(Permission.deleted_at.is_(None)) \
        .where(Organization.deleted_at.is_(None))

    __table__ = view("vw_user_permission", metadata, view_logic)
