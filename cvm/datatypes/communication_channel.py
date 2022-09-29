import dataclasses
from cvm import datatypes

__all__ = [
    'CommunicationChannel'
]

@dataclasses.dataclass(init=True)
class CommunicationChannel:
    name: str
    state: str