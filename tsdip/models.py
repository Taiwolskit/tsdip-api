from sqlalchemy import CheckConstraint, func, text
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, UUID
from sqlalchemy.orm import validates

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

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Social(Base, db.Model):
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


class RequestLog(Base, db.Model):
    request = db.Column(
        ENUM('studio', 'event', 'manager', name='request_type'),
        nullable=False,
        server_default='event'
    )
    request_id = db.Column(UUID(as_uuid=True), nullable=False)
    approve = db.Column(db.Boolean, nullable=False, server_default='False')
    approve_at = db.Column(TIMESTAMP)

    approve_by = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('manager.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    approver = db.relationship('Manager', uselist=False)


permission = db.Table(
    'permission',
    db.metadata,
    db.Column(
        'manager_id',
        UUID(as_uuid=True),
        db.ForeignKey('manager.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'studio_id',
        UUID(as_uuid=True),
        db.ForeignKey('studio.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'role',
        ENUM('owner', 'manager', 'viewer', name='permission_role'),
        nullable=False,
        server_default='viewer'
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


class Manager(Base, db.Model):
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(20), unique=True)

    studios = db.relationship(
        'Studio',
        secondary=permission,
        lazy='dynamic'
    )

    @validates('email')
    def convert_lower(self, key, value):
        return value.lower()


class Studio(Base, db.Model):
    name = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255))

    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    social = db.relationship('Social', uselist=False)


class Event(Base, db.Model):
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

    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    social = db.relationship('Social', uselist=False)
