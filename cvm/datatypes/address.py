import dataclasses
import typing
from cvm import datatypes

__all__ = [
    'Address'
]

@dataclasses.dataclass(init=True)
class Address:
    street: str
    complement: str
    district: str
    city: str
    state: str
    country: typing.Optional[datatypes.Country]
    postal_code: int

    __slots__ = (
        'street',
        'complement',
        'district',
        'city',
        'state',
        'country',
        'postal_code'
    )