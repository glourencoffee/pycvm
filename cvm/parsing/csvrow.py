import csv
from typing                 import Callable, Any, Optional
from cvm.parsing.exceptions import BadDocument

Factory = Callable[[str], Any]

def _create_or_raise(fieldname: str, factory: Factory, value: Any) -> Any:
    try:
        return factory(value)
    except ValueError as exc:
        raise BadDocument(f"failed to instantiate value '{value}' at field '{fieldname}': {exc}") from None

class CsvRow:
    def __init__(self, values):
        self.values = values

    def __getitem__(self, fieldname: str) -> str:
        try:
            return self.values[fieldname]
        except KeyError:
            raise BadDocument(f"missing CSV field '{fieldname}'") from None

    def required(self, fieldname: str, factory: Factory) -> Any:
        value = self[fieldname]
        return _create_or_raise(fieldname, factory, value)

    def optional(self, fieldname: str, factory: Factory) -> Optional[Any]:
        value = self[fieldname]

        if value == '':
            return None

        return _create_or_raise(fieldname, factory, value)