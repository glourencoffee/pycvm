import dataclasses
import datetime
import typing
from cvm import datatypes

__all__ = [
    'BookkeepingAgent'
]

@dataclasses.dataclass(init=True)
class BookkeepingAgent:
    """Implements a data structure for Item 4 of CVM Instruction 480/2009."""

    name: str
    """(4.1) 'Nome'"""

    cnpj: datatypes.CNPJ
    """(4.2) 'CNPJ'"""

    address: datatypes.Address
    """(4.3) 'Endereço'"""

    contact: datatypes.Contact
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""

    activity_started: typing.Optional[datetime.date]
    """(4.4) 'Data de início da prestação de serviço de escrituração'"""

    activity_ended: typing.Optional[datetime.date]
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""

    __slots__ = (
        'name',
        'cnpj',
        'address',
        'contact',
        'activity_started',
        'activity_ended'
    )