from enum import Enum, IntEnum


class ErrorCode(IntEnum):
    """ """
    ROUTE_AUTH_12 = 12


class ErrorMessage(Enum):
    """ """
    ROUTE_AUTH_12 = 'mmmm'


class ResponseStatus(Enum):
    """ """
    ERROR = 'error'
    SUCCESS = 'success'
    WARN = 'warn'
