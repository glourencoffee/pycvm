import dataclasses
import datetime
from cvm import datatypes

__all__ = [
    'TradingAdmission'
]

@dataclasses.dataclass(init=True, frozen=True)
class TradingAdmission:
    foreign_country: datatypes.Country
    """(1.14) 'País estrangeiro em que os valores mobiliários são admitidos à negociação'"""

    admission_date: datetime.date
    """(1.15) 'Data de admissão para negociação em país estrangeiro'"""
