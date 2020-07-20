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
    ERROR_MANAGER_9 = 109
    ERROR_MANAGER_10 = 110
    ERROR_MANAGER_11 = 111
    ERROR_MANAGER_12 = 112
    ERROR_MANAGER_13 = 113

    ERROR_STUDIO_1 = 201
    ERROR_STUDIO_2 = 202
    ERROR_STUDIO_3 = 203
    ERROR_STUDIO_4 = 204
    ERROR_STUDIO_5 = 205
    ERROR_STUDIO_6 = 206
    ERROR_STUDIO_7 = 207
    ERROR_STUDIO_8 = 208

    ERROR_EVENT_1 = 301
    ERROR_EVENT_2 = 302
    ERROR_EVENT_3 = 303
    ERROR_EVENT_4 = 304
    ERROR_EVENT_5 = 305
    ERROR_EVENT_6 = 306
    ERROR_EVENT_7 = 307
    ERROR_EVENT_8 = 308


class ErrorMessage(Enum):
    ROUTE_AUTH_0 = """Unexpected error"""

    ERROR_MANAGER_1 = """Create manager API parameters are not valid"""
    ERROR_MANAGER_2 = """The username or email had been used"""
    ERROR_MANAGER_3 = """Create manager API fail"""
    ERROR_MANAGER_4 = """Invite manager API parameters are not valid"""
    ERROR_MANAGER_5 = """The studio is not exist, cannot invite manager"""
    ERROR_MANAGER_6 = """Invite manager API fail"""
    ERROR_MANAGER_7 = """Update manager API parameters are not valid"""
    ERROR_MANAGER_8 = """The manager is not exist, cannot update"""
    ERROR_MANAGER_9 = """Update manager API fail"""
    ERROR_MANAGER_10 = """Update manager's permission API parameters are not valid"""
    ERROR_MANAGER_11 = """The manager is not exist, cannot update permission"""
    ERROR_MANAGER_12 = """The studio is not exist, cannot update permission"""
    ERROR_MANAGER_13 = """Update manager's permission API fail"""

    ERROR_STUDIO_1 = """Create studio API parameters are not valid"""
    ERROR_STUDIO_2 = """Create studio fail"""
    ERROR_STUDIO_3 = """Get studios fail"""
    ERROR_STUDIO_4 = """Update studio API parameters are not valid"""
    ERROR_STUDIO_5 = """Studio is not exist"""
    ERROR_STUDIO_6 = """Update studio API fail"""
    ERROR_STUDIO_7 = """Delete studio API parameters are not valid"""
    ERROR_STUDIO_8 = """Delete studio API fail"""

    ERROR_EVENT_1 = """Create Event API parameters are not valid"""
    ERROR_EVENT_2 = """Create Event API Studio is not exist"""
    ERROR_EVENT_3 = """Create Event API fail"""
    ERROR_EVENT_4 = """Update Event API parameters are not valid"""
    ERROR_EVENT_5 = """Update Event API Event is not exist"""
    ERROR_EVENT_6 = """Update Event API fail"""
    ERROR_EVENT_7 = """Delete Event API, event is not exist"""
    ERROR_EVENT_8 = """Delete Event API fail"""


class SuccessMessage(Enum):
    ROUTE_MANAGER_1 = """Create the manager, wait for admin approval"""
    ROUTE_MANAGER_2 = """Invite the manager, wait for the manager activation"""
    ROUTE_MANAGER_3 = """Update the manager profile success"""
    ROUTE_MANAGER_4 = """Update the manager's permission success"""

    ROUTE_STUDIO_1 = """Create ths studio success, wait for admin approval"""
    ROUTE_STUDIO_2 = """Get studios success"""
    ROUTE_STUDIO_3 = """Update ths studio success"""
    ROUTE_STUDIO_4 = """Delete the studio success"""

    ROUTE_EVENT_1 = """Create the event success, wait for admin approval"""
    ROUTE_EVENT_2 = """Update the event success"""
    ROUTE_EVENT_3 = """Delete the event success"""


class ResponseStatus(Enum):
    ERROR = 'error'
    SUCCESS = 'success'
    WARN = 'warn'
