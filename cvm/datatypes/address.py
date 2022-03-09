import dataclasses
import typing
from cvm.datatypes.federated_state import FederatedState
from cvm.datatypes.country         import Country

@dataclasses.dataclass(init=True, frozen=True)
class Address:
    street: str
    complement: str
    district: str
    city: str
    state: typing.Union[FederatedState, str]
    country: Country
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