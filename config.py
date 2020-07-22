import os


class Config():
    """Default Config Structure."""

    DEBUG = False
    TESTING = False
    FLASK_APP = os.getenv('FLASK_APP', 'flasky.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    JSON_AS_ASCII = False
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'secretkey')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'postgresql://tsdip:tsdip@tsdip-pg:5432/tsdip'
    )
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'max_overflow': 5,
        'pool_pre_ping': True,
        'pool_recycle': 30,
        'pool_size': 10,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SYSTEM_SENDER = os.getenv('SYSTEM_SENDER')


class ProductionConfig(Config):
    """Production Config Value."""

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development Config Value."""

    DEBUG = True


class TestingConfig(Config):
    """Testing Config Value."""

    TESTING = True
