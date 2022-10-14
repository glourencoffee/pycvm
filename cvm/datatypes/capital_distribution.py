from dataclasses            import dataclass
from datetime               import date
from decimal                import Decimal
from typing                 import Dict
from cvm.datatypes.security import PreferredShareType

__all__ = [
    'PreferredShareDistribution',
    'CapitalDistribution'
]

@dataclass
class PreferredShareDistribution:
    count: int
    percent: Decimal

@dataclass
class CapitalDistribution:
    individual_shareholder_count: int
    """(15.3.a) 'Número de acionistas Pessoa Física'"""

    corporation_shareholder_count: int
    """(15.3.b) 'Número de acionistas Pessoa Jurídica"""

    institutional_investor_count: int
    """(15.3.c) 'Número de investidores institucionais'"""

    outstanding_common_shares_count: int
    """(15.3.d) 'Ações ordinárias em circulação'"""

    outstanding_common_shares_percent: Decimal
    """(N/A) 'Percentual de ações ordinárias em circulação'
    
    This information is not required by the Instruction, but is provided nonetheless.
    """

    outstanding_preferred_shares_count: int
    """(15.3.d) 'Número de ações preferenciais em circulação'"""

    outstanding_preferred_shares_percent: Decimal
    """(N/A) 'Percentual de ações preferenciais em circulação'
    
    This information is not required by the Instruction, but is provided nonetheless.
    """

    outstanding_preferred_shares: Dict[PreferredShareType, PreferredShareDistribution]
    """(15.3.d) 'Número de ações preferenciais em circulação, por classe'"""

    outstanding_shares_count: int
    """(15.3.d) 'Ações em circulação'"""

    outstanding_shares_percent: Decimal
    """(N/A) 'Percentual de ações em circulação'
    
    This information is not required by the Instruction, but is provided nonetheless.
    """

    last_shareholder_meeting_date: date
    """(N/A) 'Data da última assembléia de acionistas'
    
    This information is not required by the Instruction, but is provided nonetheless.
    """