import dataclasses
import typing
from cvm.datatypes.phone import Phone

@dataclasses.dataclass(init=True, frozen=True)
class Contact:
    phone: typing.Optional[Phone]
    fax: typing.Optional[Phone]
    email: str