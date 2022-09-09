import dataclasses
import typing
from cvm import datatypes

__all__ = [
    'Address'
]

@dataclasses.dataclass(init=True, frozen=True)
class Address:
    street: str
    complement: str
    district: str
    city: str
    state: typing.Union[datatypes.FederatedState, str]
    country: datatypes.Country
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