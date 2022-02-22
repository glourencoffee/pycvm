_currency_name_table = {
    'REAL': 'BRL'
}

_currency_size_factors = {
    'UNIDADE': 1,
    'MIL': 1000
}

def normalize_currency(currency: str) -> str:
    """Returns a currency name as an ISO 4217 currency code."""

    try:
        return _currency_name_table[currency]
    except KeyError:
        raise ValueError(f"unknown currency '{ currency }'") from None

def normalize_quantity(quantity: float, currency_size: str) -> float:
    """Converts a quantity of a currency to units of that currency."""

    try:
        return quantity * _currency_size_factors[currency_size]
    except KeyError:
        raise ValueError(f"unknown currency size '{ currency_size }'")