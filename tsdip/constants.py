from enum import Enum, IntEnum


class EmailTemplate(Enum):
    SYSTEM = 'd-712300b7924444c097824187045f826e'


class ErrorCode(IntEnum):
    ROUTE_AUTH_0 = 0

    ERROR_MANAGER_1 = 101
    ERROR_MANAGER_2 = 102
    ERROR_MANAGER_3 = 103
    ERROR_MANAGER_4 = 104
    ERROR_MANAGER_5 = 105
    ERROR_MANAGER_6 = 106
    ERROR_MANAGER_7 = 107
    ERROR_MANAGER_8 = 108

    ERROR_STUDIO_1 = 201
    ERROR_STUDIO_2 = 202
    ERROR_STUDIO_3 = 203
    ERROR_STUDIO_4 = 204
    ERROR_STUDIO_5 = 205
    ERROR_STUDIO_6 = 206
    ERROR_STUDIO_7 = 207
    ERROR_STUDIO_8 = 208


class ErrorMessage(Enum):
    ROUTE_AUTH_0 = """Unexpected error"""

    ERROR_MANAGER_1 = """Create manager API parameters are not valid"""
    ERROR_MANAGER_2 = """Create manager API fail"""
    ERROR_MANAGER_3 = """Invite manager API parameters are not valid"""
    ERROR_MANAGER_4 = """Invite manager API fail"""
    ERROR_MANAGER_5 = """Update manager API parameters are not valid"""
    ERROR_MANAGER_6 = """Update manager API fail"""
    ERROR_MANAGER_7 = """Update manager's permission API parameters are not valid"""
    ERROR_MANAGER_8 = """Update manager's permission API fail"""

    ERROR_STUDIO_1 = """Create studio API parameters are not valid"""
    ERROR_STUDIO_2 = """Create studio fail"""
    ERROR_STUDIO_3 = """Get studios fail"""
    ERROR_STUDIO_4 = """Update studio API parameters are not valid"""
    ERROR_STUDIO_5 = """Studio is not exist"""
    ERROR_STUDIO_6 = """Update studio API fail"""
    ERROR_STUDIO_7 = """Delete studio API parameters are not valid"""
    ERROR_STUDIO_8 = """Delete studio API fail"""


class SuccessMessage(Enum):
    ROUTE_MANAGER_1 = """Create the manager, wait for approval"""
    ROUTE_MANAGER_2 = """Invite the manager, wait for activation"""
    ROUTE_MANAGER_3 = """Update the manager profile success"""
    ROUTE_MANAGER_4 = """Update the manager's permission success"""

    ROUTE_STUDIO_1 = """Create ths studio success"""
    ROUTE_STUDIO_2 = """Get studios success"""
    ROUTE_STUDIO_3 = """Update ths studio success"""
    ROUTE_STUDIO_4 = """Delete the studio success"""


class ResponseStatus(Enum):
    ERROR = 'error'
    SUCCESS = 'success'
    WARN = 'warn'
