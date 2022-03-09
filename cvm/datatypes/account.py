import dataclasses
import decimal
import typing

@dataclasses.dataclass(init=True, frozen=True)
class Account:
    code: str
    name: str
    quantity: decimal.Decimal
    is_fixed: bool

    @property
    def level(self) -> int:
        return self.code.count('.') + 1

    __slots__ = (
        'code',
        'name',
        'quantity',
        'is_fixed'
    )

class AccountTuple(typing.Tuple[Account]):
    def items(self) -> typing.Iterable[typing.Tuple[str, str, decimal.Decimal, bool]]:
        return ((acc.code, acc.name, acc.quantity, acc.is_fixed) for acc in self)