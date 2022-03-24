import decimal
import enum
import typing
from cvm.datatypes.account   import Account
from cvm.datatypes.statement import BalanceType
from cvm.exceptions          import BalanceLayoutError, NotImplementedException

class AccountParser:
    def parse(self, account: Account):
        pass

    def finish(self, attributes: typing.Dict[str, decimal.Decimal]):
        return

class Balance:
    __individual_layout__: typing.Sequence[typing.Tuple[str, str, str]] = []
    __consolidated_layout__: typing.Sequence[typing.Tuple[str, str, str]] = []
    __parser__ = AccountParser

    def validate(self):
        pass

def make_balance(cls, accounts: typing.Iterable[Account], balance_type: BalanceType):
    if balance_type == BalanceType.INDIVIDUAL:
        layout = cls.__individual_layout__
    else:
        layout = cls.__consolidated_layout__

    max_layout_level = max(t[0].count('.') + 1 for t in layout)
    parser           = cls.__parser__()

    accounts = iter(accounts)
    attributes = {}

    for i, (expected_code, expected_name, attr) in enumerate(layout):
        # Loop through accounts so as to "consume" non-fixed, greater-level ones,
        # as only fixed accounts whose level is <= `max_layout_level` are compared
        # against the layout.
        while True:
            try:
                acc = next(accounts)
            except StopIteration:
                raise BalanceLayoutError(f"missing account data at index {i}: too few accounts)") from None

            if acc.is_fixed and acc.level <= max_layout_level:
                if acc.code != expected_code:
                    raise BalanceLayoutError(f"invalid account code '{acc.code}' at index {i} (expected: '{expected_code}')")
                elif acc.name != expected_name:
                    raise BalanceLayoutError(f"invalid account name '{acc.name}' at index {i} (expected: '{expected_name}')")

                attributes[attr] = acc.quantity
                break
            else:
                parser.parse(acc)

    parser.finish(attributes)

    obj = cls(**attributes)

    return obj