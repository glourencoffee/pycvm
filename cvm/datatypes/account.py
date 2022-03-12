from __future__ import annotations
import dataclasses
import decimal
import typing
from cvm.datatypes.currency import Currency, CurrencySize

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

class AccountTuple:
    __slots__ = ('_currency', '_currency_size', '_accounts')

    def __init__(self, currency: Currency, currency_size: CurrencySize, accounts: typing.Sequence[Account]):
        self._currency      = currency
        self._currency_size = currency_size
        self._accounts      = tuple(accounts)

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def currency_size(self) -> CurrencySize:
        return self._currency_size

    def normalized(self) -> AccountTuple:
        """Returns a copy of `self` with `currency_size` normalized to `CurrencySize.UNIT`."""

        if self.currency_size == CurrencySize.UNIT:
            return self
        else:
            if self.currency_size != CurrencySize.THOUSAND:
                raise ValueError(f"unknown currency size '{self.currency_size}'")
            
            accounts   = []
            multiplier = 1000

            for code, name, quantity, is_fixed in self.items():
                accounts.append(Account(code, name, quantity * multiplier, is_fixed))

            return AccountTuple(self.currency, CurrencySize.UNIT, accounts)

    def items(self) -> typing.Iterable[typing.Tuple[str, str, decimal.Decimal, bool]]:
        return ((acc.code, acc.name, acc.quantity, acc.is_fixed) for acc in self)

    def __iter__(self) -> typing.Iterator[Account]:
        return iter(self._accounts)

    def __getitem__(self, index: int) -> Account:
        return self._accounts[index]