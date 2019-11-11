from sqlalchemy import CheckConstraint, func, text
from sqlalchemy.dialects.postgresql import ENUM, FLOAT, TIMESTAMP, UUID

from tsdip import db


class Base():
    """ """
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


lesson_log = db.Table(
    'lesson_log',
    db.metadata,
    db.Column(
        'course_id',
        UUID(as_uuid=True),
        db.ForeignKey('course.id', onupdate='CASCADE',
                      ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'user_id',
        UUID(as_uuid=True),
        db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'),
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


class User(Base, db.Model):
    """
    Table: user
    """
    __table_args__ = (
        CheckConstraint('age > 7'),
    )

    email = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    gender = db.Column(ENUM('secret', 'male', 'female', name='gen'))
    age = db.Column(db.Integer)
    courses = db.relationship(
        'Course',
        secondary=lesson_log,
        backref=db.backref('students', lazy='dynamic'),
        lazy='dynamic'
    )


class Social(Base, db.Model):
    fan_page = db.Column(db.String(128), nullable=False)
    instagram = db.Column(db.String(128), nullable=False)
    line = db.Column(db.String(128), nullable=False)
    website = db.Column(db.String(128), nullable=False)
    youtube = db.Column(db.String(128), nullable=False)


purchase_log = db.Table(
    'purchase_log',
    db.metadata,
    db.Column(
        'user_id',
        UUID(as_uuid=True),
        db.ForeignKey('user.id', onupdate='CASCADE',
                      ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'plan_id',
        UUID(as_uuid=True),
        db.ForeignKey('plan.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'coupon_id',
        UUID(as_uuid=True),
        db.ForeignKey('coupon.id', onupdate='CASCADE', ondelete='CASCADE'),
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


class Coupon(Base, db.Model):
    code = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Integer, nullable=False, server_default='1')
    start_at = db.Column(TIMESTAMP, nullable=False)
    end_at = db.Column(TIMESTAMP, nullable=False)


class Course(Base, db.Model):
    name = db.Column(db.String(128), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    start_at = db.Column(TIMESTAMP, nullable=False)
    end_at = db.Column(TIMESTAMP, nullable=False)
    teachter_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('teachter.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    studio_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('studio.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    students = db.relationship(
        'User',
        secondary=lesson_log,
        lazy='dynamic'
    )


rel_group_teachter = db.Table(
    'rel_group_teachter',
    db.metadata,
    db.Column(
        'dance_group_id',
        UUID(as_uuid=True),
        db.ForeignKey('dance_group.id', onupdate='CASCADE',
                      ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'teachter_id',
        UUID(as_uuid=True),
        db.ForeignKey('teachter.id', onupdate='CASCADE', ondelete='CASCADE'),
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


class DanceGroup(Base, db.Model):
    name = db.Column(db.String(128), nullable=False)
    start_at = db.Column(TIMESTAMP, nullable=False)
    end_at = db.Column(TIMESTAMP, nullable=False)
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    dancers = db.relationship(
        'Teachter',
        secondary=rel_group_teachter,
        backref=db.backref('groups', lazy='dynamic'),
        lazy='dynamic'
    )


class Event(Base, db.Model):
    name = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Integer, nullable=False, server_default='1')
    price = db.Column(db.Integer, nullable=False, server_default='0')
    start_at = db.Column(TIMESTAMP, nullable=False)
    end_at = db.Column(TIMESTAMP, nullable=False)
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )


class Plan(Base, db.Model):
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False, server_default='0')
    point = db.Column(db.Integer, nullable=False, server_default='0')
    start_at = db.Column(TIMESTAMP, nullable=False)
    end_at = db.Column(TIMESTAMP, nullable=False)
    studio_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('studio.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )


rel_studio_teachter = db.Table(
    'rel_studio_teachter',
    db.metadata,
    db.Column(
        'studio_id',
        UUID(as_uuid=True),
        db.ForeignKey('studio.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    ),
    db.Column(
        'teachter_id',
        UUID(as_uuid=True),
        db.ForeignKey('teachter.id', onupdate='CASCADE', ondelete='CASCADE'),
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


class Teachter(Base, db.Model):
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    studios = db.relationship(
        'Studio',
        secondary=rel_studio_teachter,
        backref=db.backref('teachters', lazy='dynamic'),
        lazy='dynamic'
    )


class Studio(Base, db.Model):
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)

    social_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('social.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
