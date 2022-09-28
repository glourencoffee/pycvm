from enum import IntEnum, auto

__all__ = [
    'RegistrationCategory',
    'RegistrationStatus'
]

class RegistrationCategory(IntEnum):
    A       = auto()
    B       = auto()
    UNKNOWN = auto()

class RegistrationStatus(IntEnum):
    ACTIVE         = auto()
    UNDER_ANALYSIS = auto()
    NOT_GRANTED    = auto()
    SUSPENDED      = auto()
    CANCELED       = auto()