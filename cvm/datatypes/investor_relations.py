import dataclasses
import datetime
import typing
from cvm import datatypes

class InvestorRelationsOfficerType(datatypes.DescriptiveIntEnum):
    INVESTOR_RELATIONS_OFFICER = (1, 'Diretor de relações com investidores')
    LIQUIDATOR                 = (2, 'Liquidante')
    JUDICIAL_ADMINISTRATOR     = (3, 'Administrador judicial')
    TRUSTEE                    = (4, 'Gestor judicial')
    SYNDIC                     = (5, 'Síndico')
    LEGAL_REPRESENTATIVE       = (6, 'Representante legal (para emissores estrangeiros)')

@dataclasses.dataclass(init=True, frozen=True)
class InvestorRelationsOfficer:
    """Implements a data structure for Item 5 of CVM Instruction 480/2009."""

    type: InvestorRelationsOfficerType
    """(5.1) 'Tipo de responsável'"""

    name: str
    """(5.2) 'Nome'"""

    cpf: datatypes.CPF
    """(5.3) 'CPF ou CNPJ'
    
    Note: Although this Instruction considers CNPJ, the actual CVM database only stores CPF.
    """

    address: datatypes.Address
    """(5.5) 'Endereço'"""

    contact: datatypes.Contact
    """(5.4, 5.6, 5.7, 5.8, 5.9) Contact info"""

    activity_started: typing.Optional[datetime.date]
    """(5.10) 'Data de início da condição de responsável'"""

    activity_ended: typing.Optional[datetime.date]
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""

    __slots__ = (
        'type',
        'name',
        'cpf',
        'address',
        'contact',
        'activity_started',
        'activity_ended'
    )
