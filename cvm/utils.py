import datetime

def date_from_string(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

def date_to_string(date: datetime.time) -> str:
    return date.strftime('%Y-%m-%d')

def normalize_quantity(quantity: float, currency_size: str) -> float:
    """Converts a quantity of a currency to units of that currency."""

    try:
        return quantity * _currency_size_factors[currency_size]
    except KeyError:
        raise ValueError(f"unknown currency size '{ currency_size }'")