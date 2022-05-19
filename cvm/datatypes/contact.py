import dataclasses
import typing
from cvm import datatypes

@dataclasses.dataclass(init=True, frozen=True)
class Contact:
    phone: typing.Optional[datatypes.Phone]
    fax: typing.Optional[datatypes.Phone]
    email: str