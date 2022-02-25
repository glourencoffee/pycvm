import zlib
from typing                  import List, Tuple, Iterable
from pprint                  import pformat
from cvm.parsing.dfp.account import Account

class Balance:
    _layout: List[Tuple[str, str, str]] = []
    
    __slots__ = []

    def __init__(self, accounts: Iterable[Account]):
        max_layout_level = max(t[0].count('.') + 1 for t in self._layout)

        for i, (expected_code, expected_name, attr) in enumerate(self._layout):
            if attr not in self.__slots__:
                raise AttributeError(f"invalid attribute '{ attr }'")

            # Loop through accounts so as to "consume" non-fixed, greater-level ones,
            # as only fixed accounts whose level is <= `max_layout_level` are compared
            # against the layout.
            while True:
                try:
                    acc = next(accounts)
                except StopIteration:
                    raise ValueError(f"missing account data at index { i }: too few accounts given)") from None

                if acc.is_fixed and acc.level <= max_layout_level:
                    if acc.code != expected_code:
                        raise ValueError(f"invalid account code '{ acc.code }' at index { i } (expected: '{ expected_code }')")
                    elif acc.name != expected_name:
                        raise ValueError(f"invalid account name '{ acc.name }' at index { i } (expected: '{ expected_name }')")

                    setattr(self, attr, acc.quantity)
                    break
                else:
                    self.parse_other(acc)

    def validate(self):
        pass

    def parse_other(self, account: Account):
        pass

    def __str__(self) -> str:
        obj = {attr: getattr(self, attr) for attr in self.__slots__}
        return pformat(obj)