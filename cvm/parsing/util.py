import datetime
import pandas as pd
from typing import Callable, Any, Dict, Generator, List

_currency_name_table = {
    'REAL': 'BRL'
}

_currency_size_factors = {
    'UNIDADE': 1,
    'MIL': 1000
}

def date_from_string(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

def cnpj_to_int(cnpj: str) -> int:
    integral_cnpj = ''.join(c for c in cnpj if c.isdigit())
    
    return int(integral_cnpj)

def cnpj_to_str(cnpj: int) -> int:
    zero_padded_cnpj = f'{cnpj:014}'

    lengths    = (2, 3, 3, 4, 2)
    separators = '../-\0'
    start      = 0
    cnpj       = ''

    for length, sep in zip(lengths, separators):
        stop  = start + length
        part  = zero_padded_cnpj[start:stop]
        cnpj += part + sep
        start = stop

    return cnpj.rstrip('\0')

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

def read_required(row: Dict[str, str], fieldname: str, instantiator: Callable[[str], Any]):
    return instantiator(row[fieldname])

def read_optional(row: Dict[str, str], fieldname: str, instantiator: Callable[[str], Any]):
    try:
        value = row[fieldname]

        if value == '':
            return None
        
        return instantiator(value)
    except KeyError:
        return None

def value_error_instantiator(underlying_instantiator, default = None):
    def wrapper(value):
        try:
            return underlying_instantiator(value)
        except ValueError:
            return default

    return wrapper

def dataframe_from_reader(reader: Generator[Any, None, None], csv_file: str, delimiter: str, attributes: List[str]) -> pd.DataFrame:
    data = []

    for obj in reader(csv_file, delimiter):
        data_row = []

        for attr in attributes:
            value = getattr(obj, attr)

            if value is not None:
                value = str(value)

            data_row.append(value)

        data.append(data_row)
    
    return pd.DataFrame(data=data, columns=attributes)