class Account:
    code: str
    name: str
    quantity: float
    is_fixed: bool

    @property
    def level(self) -> int:
        return self.code.count('.') + 1

    def __str__(self) -> str:
        return f'Account({ self.code }, { self.name }, { self.quantity }, fixed: { self.is_fixed })'