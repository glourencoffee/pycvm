import zlib
from typing import List, Tuple, Iterable

AccountList = List[Tuple[str, str, float]]

class Balance:
    _layout: List[Tuple[str, str, str]] = []
    
    __slots__ = []

    def __init__(self, accounts: AccountList):
        for i, (expected_code, expected_name, attr) in enumerate(self._layout):
            if attr not in self.__slots__:
                raise AttributeError(f"invalid attribute '{ attr }'")

            try:
                code, name, quantity = next(accounts)
            except (IndexError, StopIteration):
                raise ValueError(f"missing account data at index { i }: too few accounts given)") from None

            if code != expected_code:
                raise ValueError(f"invalid account code '{ code }' at index { i } (expected: '{ expected_code }')")
            elif name != expected_name:
                raise ValueError(f"invalid account name '{ name }' at index { i } (expected: '{ expected_name }')")

            setattr(self, attr, float(quantity))

    def validate(self):
        pass

def hash_id(layout: Iterable[Tuple[str, str]]) -> int:
    hash_str = ''.join(account_code + account_name for account_code, account_name in layout)
    
    return zlib.crc32(hash_str.encode('utf-8'))