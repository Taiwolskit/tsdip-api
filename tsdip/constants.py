from enum import Enum, IntEnum


class ErrorCode(IntEnum):
    """ """
    ROUTE_AUTH_0 = 0
    ERROR_STUDIO_1 = 1
    ERROR_STUDIO_2 = 2
    ERROR_STUDIO_3 = 3


class ErrorMessage(Enum):
    """ """
    ROUTE_AUTH_0 = 'Unexpected error'
    ERROR_STUDIO_1 = 'API parameters are not valid'
    ERROR_STUDIO_2 = 'Create studio fail'
    ERROR_STUDIO_3 = 'Get studios fail'


class SuccessMessage(Enum):
    """ """
    ROUTE_AUTH_1 = 'Create studio success'
    ROUTE_AUTH_2 = 'Get studios success'


class ResponseStatus(Enum):
    """ """
    ERROR = 'error'
    SUCCESS = 'success'
    WARN = 'warn'
