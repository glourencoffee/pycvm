import dataclasses
import typing
from cvm import datatypes

__all__ = [
    'Contact'
]

@dataclasses.dataclass(init=True, frozen=True)
class Contact:
    phone: typing.Optional[datatypes.Phone]
    fax: typing.Optional[datatypes.Phone]
    email: str