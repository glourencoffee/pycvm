class Account:
    __slots__ = [
        '_code',
        '_name',
        '_quantity',
        '_is_fixed'
    ]

    def __init__(self, code: str, name: str, quantity: float, is_fixed: bool):
        self._code     = code
        self._name     = name
        self._quantity = quantity
        self._is_fixed = is_fixed

    @property
    def code(self) -> str:
        return self._code

    @property
    def name(self) -> str:
        return self._name

    @property
    def quantity(self) -> float:
        return self._quantity

    @property
    def is_fixed(self) -> bool:
        return self._is_fixed

    @property
    def level(self) -> int:
        return self.code.count('.') + 1

    def __repr__(self) -> str:
        return f"<Account code={self.code} name='{self.name}' quantity={self.quantity} fixed={self.is_fixed}>"