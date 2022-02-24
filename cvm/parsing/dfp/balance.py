import zlib
from typing import List, Tuple, Optional, Iterable

AccountList = List[Tuple[str, str, float]]

class Balance:
    _layout: List[Tuple[str, str, Optional[str]]] = []
    
    __slots__ = []

    def __init__(self, accounts: AccountList):
        for i, (code, name, quantity) in enumerate(accounts):
            try:
                expected_code, expected_name, attr = self._layout[i]
            except IndexError:
                raise ValueError(f"invalid account data: index { i } out of layout's bounds)") from None

            if code != expected_code:
                raise ValueError(f"invalid account code '{ code }' at index { i } (expected: '{ expected_code }')")
            elif name != expected_name:
                raise ValueError(f"invalid account name '{ name }' at index { i } (expected: '{ expected_name }')")
            
            if attr not in self.__slots__:
                raise ValueError(f'invalid attribute { attr }')

            setattr(self, attr, float(quantity))

    def validate(self):
        pass

def hash_id(layout: Iterable[Tuple[str, str]]) -> int:
    hash_str = ''.join(account_code + account_name for account_code, account_name in layout)
    
    return zlib.crc32(hash_str.encode('utf-8'))