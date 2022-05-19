import dataclasses
from cvm import datatypes

@dataclasses.dataclass(init=True, frozen=True)
class CommunicationChannel:
    name: str
    state: datatypes.FederatedState