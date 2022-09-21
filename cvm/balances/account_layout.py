from __future__ import annotations
import datetime
import enum
import typing
from cvm.balances.industrial.cvm_codes import cvm_codes as industrial_cvm_codes
from cvm.balances.financial.cvm_codes  import cvm_codes as financial_cvm_codes
from cvm.balances.insurance.cvm_codes  import cvm_codes as insurance_cvm_codes
from cvm                               import exceptions, datatypes

__all__ = [
    'AccountLayoutType',
    'AccountLayout',
    'AccountLayoutValidator',
    'industrial_cvm_codes',
    'financial_cvm_codes',
    'insurance_cvm_codes'
]

class AccountLayoutType(enum.IntEnum):
    INDUSTRIAL = 0
    FINANCIAL  = 1
    INSURANCE  = 2

    @staticmethod
    def from_cvm_code(cvm_code: str) -> AccountLayoutType:
        if cvm_code in industrial_cvm_codes():
            return AccountLayoutType.INDUSTRIAL

        elif cvm_code in financial_cvm_codes():
            return AccountLayoutType.FINANCIAL
        
        elif cvm_code in insurance_cvm_codes():
            return AccountLayoutType.INSURANCE

        else:
            raise ValueError(f'no account layout was found for CVM code {cvm_code}')

class AccountLayout:
    __slots__ = (
        '_first_year',
        '_last_year',
        '_max_level',
        '_account_info'
    )

    def __init__(self, first_year: int, last_year: typing.Optional[int] = None):
        self._first_year = first_year
        self._last_year  = last_year
        self._max_level  = 0
        self._account_info: typing.Dict[str, typing.Tuple[str, typing.Optional[str]]] = {}

    def add(self, expected_code: str, expected_name: str, attr_name: typing.Optional[str] = None):
        self._account_info[expected_code] = (expected_name, attr_name)

        account_level   = expected_code.count('.') + 1
        self._max_level = max(self._max_level, account_level)

    @property
    def first_year(self) -> int:
        return self._first_year
    
    @property
    def last_year(self) -> typing.Optional[int]:
        return self._last_year

    @property
    def max_level(self) -> int:
        return self._max_level

    def __iter__(self):
        return (
            (expected_code, expected_name, attr_name)
            for expected_code, (expected_name, attr_name) in self._account_info.items()
        )

class AccountLayoutValidator:
    def individual_layouts(self) -> typing.Iterable[AccountLayout]:
        raise exceptions.NotImplementedException(self.__class__, 'individual_layouts')

    def consolidated_layouts(self) -> typing.Iterable[AccountLayout]:
        raise exceptions.NotImplementedException(self.__class__, 'consolidated_layouts')

    def validate(self,
                 accounts: typing.Sequence[datatypes.Account],
                 balance_type: datatypes.BalanceType,
                 reference_date: datetime.date
    ) -> typing.Dict[str, int]:

        if balance_type == datatypes.BalanceType.INDIVIDUAL:
            layouts = self.individual_layouts()
        else:
            layouts = self.consolidated_layouts()

        reference_year = reference_date.year

        for l in layouts:
            if reference_year < l.first_year:
                continue

            if l.last_year is not None and reference_year > l.last_year:
                continue

            return self._validate_layout(accounts, l)

        raise exceptions.AccountLayoutError('no layout found for period')

    def _prepare(self):
        pass

    def _process(self, code: str, name: str, quantity: int, is_fixed: bool):
        pass

    def _finish(self, attributes: typing.Dict[str, int]):
        return

    def _validate_layout(self,
                        accounts: typing.Sequence[datatypes.Account],
                        layout: AccountLayout
    ) -> typing.Dict[str, int]:

        accounts = iter(accounts)
        attributes = {}

        self._prepare()

        for i, (expected_code, expected_name, attr) in enumerate(layout):

            # Loop through accounts so as to "consume" non-fixed, greater-level ones,
            # as only fixed accounts whose level is <= `layout.max_level` are compared
            # against the layout.
            while True:
                try:
                    acc: datatypes.Account = next(accounts)
                except StopIteration:
                    raise exceptions.AccountLayoutError(f"missing account data at index {i}: too few accounts)") from None

                if acc.is_fixed and acc.level <= layout.max_level:
                    if acc.code != expected_code:
                        raise exceptions.AccountLayoutError(
                            f"invalid account code '{acc.code}' - '{acc.name}' at index {i} (expected: '{expected_code}' - '{expected_name}')"
                        )

                    if attr is not None:
                        attributes[attr] = int(acc.quantity)

                    break
                else:
                    self._process(acc.code, acc.name, int(acc.quantity), acc.is_fixed)

        self._finish(attributes)

        return attributes