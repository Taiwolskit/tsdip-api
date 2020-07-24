from datetime import datetime

from sqlalchemy import CheckConstraint, func, text
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, UUID
from sqlalchemy.orm import validates
from sqlalchemy.sql import expression

from tsdip import db

ORG_FOREKEY_FIELD = 'organization.id'
USER_FOREKEY_FIELD = 'user.id'


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

    def update(self, **kwargs):
        """ORM model base update function."""
        for key, value in kwargs.items():
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

    email = db.Column(db.String(255), unique=True)
    fan_page = db.Column(db.String(255), unique=True)
    instagram = db.Column(db.String(255), unique=True)
    line = db.Column(db.String(255), unique=True)
    telephone = db.Column(db.String(20), unique=True)
    website = db.Column(db.String(255), unique=True)
    youtube = db.Column(db.String(255), unique=True)

    @validates('email', 'fan_page', 'instagram', 'line', 'telephone', 'website', 'youtube')
    def convert_lower(self, key, value):
        """Convert field to lower case."""
        return value.lower()


class Event(db.Model, Base):
    """ORM Event model."""

    __table_args__ = (
        CheckConstraint('amount > -1'),
        CheckConstraint('price > -1'),
    )

    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    amount = db.Column(db.Integer, nullable=False, server_default='0')
    price = db.Column(db.Integer, nullable=False, server_default='0')
    reg_link = db.Column(db.String(128), unique=True)
    reg_start_at = db.Column(TIMESTAMP)
    reg_end_at = db.Column(TIMESTAMP)
    start_at = db.Column(TIMESTAMP)
    end_at = db.Column(TIMESTAMP)

    org_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(ORG_FOREKEY_FIELD, onupdate='CASCADE',
                      ondelete='CASCADE'),
        nullable=False
    )
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE')
    )

    org = db.relationship('Organization', uselist=False)
    social = db.relationship('Social', uselist=False)
    requests = db.relationship('RequestEventLog', lazy=True)


class Organization(db.Model, Base):
    """ORM Organization model."""

    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    org_type = db.Column(
        ENUM('dance_group', 'studio', name='org_type'),
        nullable=False,
        server_default='studio'
    )
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE')
    )

    social = db.relationship('Social', uselist=False)
    events = db.relationship('Event', lazy=True)
    requests = db.relationship('RequestOrgLog', lazy=True)


class Permission(db.Model, Base):
    """ORM Permission model."""

    could_invite = db.Column(db.Boolean, nullable=False,
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
                      ondelete='CASCADE'),
        nullable=False
    )
    permission_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('permission.id', onupdate='CASCADE', ondelete='CASCADE'),
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
                      ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'role_id',
        UUID(as_uuid=True),
        db.ForeignKey('role.id', onupdate='CASCADE', ondelete='CASCADE'),
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
    orgRequests = db.relationship('RequestOrgLog', lazy=True)
    eventRequests = db.relationship('RequestEventLog', lazy=True)
    inviteRequests = db.relationship(
        'RequestMemberLog', lazy=True, foreign_keys='RequestMemberLog.inviter_id')
    inviteeRequests = db.relationship(
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
                      ondelete='CASCADE'),
        nullable=False
    )
    applicant_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    approver_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('manager.id', onupdate='CASCADE', ondelete='CASCADE')
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
        db.ForeignKey('event.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    applicant_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    approver_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('manager.id', onupdate='CASCADE', ondelete='CASCADE')
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
                      ondelete='CASCADE'),
        nullable=False
    )
    inviter_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    invitee_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(USER_FOREKEY_FIELD,
                      onupdate='CASCADE', ondelete='CASCADE')
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

    __tablename__ = 'manager'

    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(20), unique=True)

    @validates('email', 'username')
    def convert_lower(self, key, value):
        """Convert field to lower case."""
        return value.lower()
