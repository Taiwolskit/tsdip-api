from sqlalchemy import CheckConstraint, func, text
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, UUID
from sqlalchemy.orm import validates
from sqlalchemy.sql import expression

from tsdip import db


class Base():
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
        for key, value in kwargs.items():
            setattr(self, key, value)

    def as_dict(self, filter_at=False):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if filter_at:
            del temp['created_at']
            del temp['updated_at']
            del temp['deleted_at']

        return temp


class Social(db.Model, Base):
    email = db.Column(db.String(255), unique=True)
    fan_page = db.Column(db.String(255), unique=True)
    instagram = db.Column(db.String(255), unique=True)
    line = db.Column(db.String(255), unique=True)
    telephone = db.Column(db.String(20), unique=True)
    website = db.Column(db.String(255), unique=True)
    youtube = db.Column(db.String(255), unique=True)

    @validates('email', 'fan_page', 'instagram', 'line', 'telephone', 'website', 'youtube')
    def convert_lower(self, key, value):
        return value.lower()


class Event(db.Model, Base):
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
        db.ForeignKey('organization.id', onupdate='CASCADE',
                      ondelete='CASCADE')
    )
    ogr = db.relationship('Organization', uselist=False)
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    social = db.relationship('Social', uselist=False)


class Organization(db.Model, Base):
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


class Permission(db.Model, Base):
    could_invite = db.Column(db.Boolean, nullable=False,
                             server_default=expression.false())


class Role(db.Model, Base):
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
        db.ForeignKey('organization.id', onupdate='CASCADE',
                      ondelete='CASCADE')
    )
    permission_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('permission.id', onupdate='CASCADE', ondelete='CASCADE')
    )

    org = db.relationship('Organization', uselist=False)
    permission = db.relationship('Permission', uselist=False)


user_role = db.Table(
    'user_role',
    db.metadata,
    db.Column(
        'user_id',
        UUID(as_uuid=True),
        db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'),
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
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(20), unique=True)

    roles = db.relationship('UserRole', secondary=user_role, lazy='dynamic')

    @validates('email')
    def convert_lower(self, key, value):
        return value.lower()


class RequestOrgLog(db.Model, Base):
    req_type = db.Column(db.String(255), nullable=False)
    org_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('organization.id', onupdate='CASCADE',
                      ondelete='CASCADE')
    )
    applicant_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE')
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
    req_type = db.Column(db.String(255), nullable=False)
    event_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('event.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    applicant_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE')
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
    req_type = db.Column(db.String(255), nullable=False)
    inviter_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    invitee_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    invited_at = db.Column(TIMESTAMP)

    inviter = db.relationship('User', uselist=False)
    invitee = db.relationship('User', uselist=False)


class Manager(db.Model, Base):
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(20), unique=True)

    @validates('email')
    def convert_lower(self, key, value):
        return value.lower()
