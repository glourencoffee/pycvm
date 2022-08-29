import dataclasses
import datetime
import typing
from cvm import datatypes

@dataclasses.dataclass(init=True, frozen=True)
class Auditor:
    """Implements a data structure for Item 3 of CVM Instruction 480/2009."""

    name: str
    """(3.1) 'Nome'"""

    tax_id: datatypes.TaxID
    """(3.2) 'CNPJ/CPF'"""

    cvm_code: str
    """(N/A) This data item is not required by CVM, but is provided nonetheless."""

    activity_started: datetime.date
    """(3.3) 'Data de início da prestação de serviço'"""

    activity_ended: typing.Optional[datetime.date]
    """(N/A) This data item is not required by CVM, but is provided nonetheless."""

    technical_manager_name: str
    """(3.4) 'Responsável técnico'"""

    technical_manager_cpf: datatypes.CPF
    """(3.5) 'CPF do responsável técnico'"""

    technical_manager_activity_started: datetime.date
    """(N/A) This data item is not required by CVM, but is provided nonetheless."""

    technical_manager_activity_ended: typing.Optional[datetime.date]
    """(N/A) This data item is not required by CVM, but is provided nonetheless."""

    __slots__ = (
        'name',
        'tax_id',
        'cvm_code',
        'activity_started',
        'activity_ended',
        'technical_manager_name',
        'technical_manager_cpf',
        'technical_manager_activity_started',
        'technical_manager_activity_ended'
    )