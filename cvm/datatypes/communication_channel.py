import dataclasses
from cvm.datatypes.federated_state import FederatedState

@dataclasses.dataclass(init=True, frozen=True)
class CommunicationChannel:
    name: str
    state: FederatedState