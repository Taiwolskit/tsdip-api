from enum import Enum, IntEnum


class EmailTemplate(Enum):
    """Email template ID list."""

    SYSTEM = 'd-712300b7924444c097824187045f826e'


class ErrorCode(IntEnum):
    """Response error code list."""

    DEFAULT_ERROR = 100
    PARAM_SCHEMA_WARN = 101
    API_FAILED = 102
    AUTH_API_TOKEN_ERROR = 103
    JWT_USER_NOT_EXIST = 104

    @classmethod
    def _missing_(cls, value):
        return cls[value] if value in cls._member_names_ else ErrorCode.DEFAULT_ERROR


class ErrorMessage(Enum):
    """Response error message list."""

    DEFAULT_ERROR = 'Unexpected error'
    PARAM_SCHEMA_WARN = """The API's parameters are invalid"""
    API_FAILED = 'API process failed'
    AUTH_API_TOKEN_ERROR = 'API token is invalid'
    JWT_USER_NOT_EXIST = 'Token is invalid, user is not exist'

    @classmethod
    def _missing_(cls, value):
        return cls[value] if value in cls._member_names_ else ErrorMessage.DEFAULT_ERROR


class SuccessMessage(Enum):
    """Response success message list."""

    API_SUCCESS = 'API success'
    MANAGER_API_SUCCESS = 'The manager API success'
    USER_API_SUCCESS = 'The user API success'
    ORG_API_SUCCESS = 'The organization API success'
    EVENT_API_SUCCESS = 'The event API success'

    @classmethod
    def _missing_(cls, value):
        return cls[value] if value in cls._member_names_ else SuccessMessage.API_SUCCESS


class ResponseStatus(Enum):
    """Response status list."""

    ERROR = 'error'
    INFO = 'info'
    SUCCESS = 'success'
    WARN = 'warn'

    @classmethod
    def _missing_(cls, value):
        return cls[value] if value in cls._member_names_ else ResponseStatus.ERROR
