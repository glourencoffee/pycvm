import dataclasses
import datetime
import typing
from cvm import datatypes

@dataclasses.dataclass(init=True, frozen=True)
class ShareholderDepartmentPerson:
    name: str
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""

    address: datatypes.Address
    """(6.1) 'Endereço'"""

    contact: datatypes.Contact
    """(6.2, 6.3, 6.4, 6.5, 6.6) Contact info"""

    activity_started: typing.Optional[datetime.date]
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""
    
    activity_ended: typing.Optional[datetime.date]
    """(N/A) This information is not required by the Instruction, but is provided nonetheless."""
