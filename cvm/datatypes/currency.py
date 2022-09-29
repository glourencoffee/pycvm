from enum import IntEnum, auto

__all__ = [
    'Currency',
    'CurrencySize'
]

class Currency(IntEnum):
    BRL = auto()

class CurrencySize(IntEnum):
    UNIT     = 1
    THOUSAND = 1000