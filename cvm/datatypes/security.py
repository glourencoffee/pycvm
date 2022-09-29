import dataclasses
import datetime
import typing
from enum import IntEnum, auto
from cvm  import datatypes

__all__ = [
    'SecurityType',
    'MarketType',
    'MarketSegment',
    'PreferredShareType',
    'Security'
]

class SecurityType(IntEnum):
    STOCK                               = auto()
    DEBENTURE                           = auto()
    CONVERTIBLE_DEBENTURE               = auto()
    SUBCRIPTION_BONUS                   = auto()
    PROMISSORY_NOTE                     = auto()
    COLLECTIVE_INVESTMENT_CONTRACT      = auto()
    SECURITIES_DEPOSITORY_RECEIPT       = auto()
    REAL_ESTATE_RECEIVABLE_CERTIFICATE  = auto()
    AGRIBUSINESS_RECEIVABLE_CERTIFICATE = auto()
    COLLECTIVE_INVESTMENT_BOND          = auto()
    FINANCIAL_BILLS                     = auto()
    UNREGISTERED_SECURITY               = auto()
    UNITS                               = auto()
    PREFERRED_SHARES                    = auto()

class MarketType(IntEnum):
    NON_ORGANIZED_OTC = auto()
    ORGANIZED_OTC     = auto()
    STOCK_EXCHANGE    = auto()

class MarketSegment(IntEnum):
    NEW_MARKET              = auto()
    CORPORATE_GOVERNANCE_L1 = auto()
    CORPORATE_GOVERNANCE_L2 = auto()
    BOVESPA_PLUS            = auto()
    BOVESPA_PLUS_L2         = auto()

class PreferredShareType(IntEnum):
    PNA = auto()
    PNB = auto()
    PNC = auto()
    PNU = auto()

@dataclasses.dataclass(init=True)
class Security:
    type: SecurityType
    """(2.1.a) 'Nome'"""

    market_type: MarketType
    """(2.1.b) 'Mercado no qual os valores mobiliários são negociados'"""

    market_managing_entity_symbol: str
    """(2.1.c) 'Entidade administradora do mercado no qual os valores mobiliários são admitidos à
    negociação, informando o código de negociação de cada espécie ou classe de ações admitidas
    à negociação'"""

    market_managing_entity_name: str
    """(2.1.c)"""

    preferred_share_type: typing.Optional[PreferredShareType]
    """(2.1.c)"""

    bdr_unit_composition: str
    """(2.1.c)"""

    trading_symbol: str
    """(2.1.c) Also known as 'ticker'"""
    
    trading_started: typing.Optional[datetime.date]
    """(2.1.d) 'Data de início da negociação'"""

    trading_ended: typing.Optional[datetime.date]
    """(N/A) This data item is not required by CVM, but is provided nonetheless."""

    market_segment: typing.Optional[MarketSegment]
    """(2.1.e) 'Se houver, indicar o segmento de negociação do mercado organizado'"""

    listing_started: typing.Optional[datetime.date]
    """(2.1.f) 'Data de início da listagem no segmento de negociação'"""

    listing_ended: typing.Optional[datetime.time]
    """(N/A) This data item is not required by CVM, but is provided nonetheless."""
