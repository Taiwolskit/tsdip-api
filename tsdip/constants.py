from enum import Enum, IntEnum


class ErrorCode(IntEnum):
    """ """
    ROUTE_AUTH_1 = 1
    ROUTE_AUTH_12 = 12
    ROUTE_AUTH_2 = 2


class ErrorMessage(Enum):
    """ """
    ROUTE_AUTH_1 = 'API parameters are not valid'
    ROUTE_AUTH_12 = 'mmmm'
    ROUTE_AUTH_2 = 'Create studio fail'


class SuccessMessage(Enum):
    """ """
    ROUTE_AUTH_1 = 'Create studio success'


class ResponseStatus(Enum):
    """ """
    ERROR = 'error'
    SUCCESS = 'success'
    WARN = 'warn'
