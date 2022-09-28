from enum import IntEnum, auto

__all__ = [
    'ControllingInterest'
]

class ControllingInterest(IntEnum):
    GOVERNMENTAL         = auto()
    GOVERNMENTAL_HOLDING = auto()
    FOREIGN              = auto()
    FOREIGN_HOLDING      = auto()
    PRIVATE              = auto()
    PRIVATE_HOLDING      = auto()