import os


class Config():
    """ """
    DEBUG = False
    TESTING = False
    FLASK_APP = os.getenv('FLASK_APP', 'flasky.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
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


class ProductionConfig(Config):
    """ """
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """ """
    DEBUG = True


class TestingConfig(Config):
    """ """
    TESTING = True
