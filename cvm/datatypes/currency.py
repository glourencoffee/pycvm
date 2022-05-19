from cvm import datatypes

class Currency(datatypes.DescriptiveIntEnum):
    BRL = (1, 'Real')

class CurrencySize(datatypes.DescriptiveIntEnum):
    UNIT     = (1, 'Unidade')
    THOUSAND = (2, 'Mil')