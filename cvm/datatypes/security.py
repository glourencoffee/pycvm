import dataclasses
import datetime
import typing
from cvm import datatypes

__all__ = [
    'SecurityType',
    'MarketType',
    'MarketSegment',
    'PreferredShareType',
    'Security'
]

class SecurityType(datatypes.DescriptiveIntEnum):
    STOCK                               = (1,  'Ações Ordinárias')
    DEBENTURE                           = (2,  'Debêntures')
    CONVERTIBLE_DEBENTURE               = (3,  'Debêntures conversíveis')
    SUBCRIPTION_BONUS                   = (4,  'Bônus de subscrição')
    PROMISSORY_NOTE                     = (5,  'Nota comercial')
    COLLECTIVE_INVESTMENT_CONTRACT      = (6,  'Contrato de investimento coletivo')
    SECURITIES_DEPOSITORY_RECEIPT       = (7,  'Certificados de depósito de valores mobiliários')
    REAL_ESTATE_RECEIVABLE_CERTIFICATE  = (8,  'Certificados de recebíveis imobiliários')
    AGRIBUSINESS_RECEIVABLE_CERTIFICATE = (9,  'Certificado de recebíveis do agronegócio')
    COLLECTIVE_INVESTMENT_BOND          = (10, 'Título de investimento coletivo')
    FINANCIAL_BILLS                     = (11, 'Letras Financeiras')
    UNREGISTERED_SECURITY               = (12, 'Valor Mobiliário Não Registrado')
    UNITS                               = (13, 'Units')
    PREFERRED_SHARES                    = (14, 'Ações Preferenciais')

class MarketType(datatypes.DescriptiveIntEnum):
    NON_ORGANIZED_OTC = (1, 'Balcão não-organizado')
    ORGANIZED_OTC     = (2, 'Balcão organizado')
    STOCK_EXCHANGE    = (3, 'Bolsa')

    @property
    def is_organized(self) -> bool:
        return self.value != MarketType.NON_ORGANIZED_OTC

class MarketSegment(datatypes.DescriptiveIntEnum):
    NEW_MARKET                      = (1, 'Novo Mercado')
    CORPORATE_GOVERNANCE_L1         = (2, 'Nível 1')
    CORPORATE_GOVERNANCE_L2         = (3, 'Nível 2')
    BOVESPA_PLUS                    = (4, 'Bovespa Mais')
    BOVESPA_PLUS_L2                 = (5, 'Bovespa Mais Nível 2')

class PreferredShareType(datatypes.DescriptiveIntEnum):
    PNA = (1, 'Preferencial Classe A')
    PNB = (2, 'Preferencial Classe B')
    PNC = (3, 'Preferencial Classe C')
    PNU = (4, 'Preferencial Classe U')

@dataclasses.dataclass(init=True, frozen=True)
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
