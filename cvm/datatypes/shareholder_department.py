import dataclasses
import datetime
import typing
from cvm.datatypes.address import Address
from cvm.datatypes.contact import Contact

@dataclasses.dataclass(init=True, frozen=True)
class ShareholderDepartmentPerson:
    name: str
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""

    address: Address
    """(6.1) 'Endereço'"""

    contact: Contact
    """(6.2, 6.3, 6.4, 6.5, 6.6) Contact info"""

    activity_started: typing.Optional[datetime.date]
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""
    
    activity_ended: typing.Optional[datetime.date]
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""
