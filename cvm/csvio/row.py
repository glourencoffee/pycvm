import typing
from cvm.exceptions import MissingValueError, InvalidValueError

class CSVRow:
    __slots__ = ('values',)

    def __init__(self, values):
        self.values = values

    def __getitem__(self, fieldname: str) -> str:
        try:
            return self.values[fieldname]
        except KeyError:
            raise MissingValueError(f"missing field '{fieldname}'") from None

    def required(self,
                 fieldname: str,
                 factory: typing.Callable[[str], typing.Any],
                 allow_empty_string: bool = False
    ) -> typing.Any:
        value = self[fieldname]

        if value == '' and not allow_empty_string:
            raise MissingValueError(f"got empty string at field '{fieldname}'")

        try:
            return factory(value)
        except ValueError as exc:
            raise InvalidValueError(f"failed to create object from value '{value}' at field '{fieldname}': {exc}") from None

    def optional(self,
                 fieldname: str,
                 factory: typing.Callable[[str], typing.Any],
                 allow_empty_string: bool = True
    ) -> typing.Optional[typing.Any]:

        value = self[fieldname]

        if value == '' and not allow_empty_string:
            return None

        try:
            return factory(value)
        except ValueError:
            return None