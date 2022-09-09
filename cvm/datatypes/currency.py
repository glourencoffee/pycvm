from cvm import datatypes

__all__ = [
    'Currency',
    'CurrencySize'
]

class Currency(datatypes.DescriptiveIntEnum):
    BRL = (1, 'Real')

class CurrencySize(datatypes.DescriptiveIntEnum):
    UNIT     = (1, 'Unidade')
    THOUSAND = (2, 'Mil')