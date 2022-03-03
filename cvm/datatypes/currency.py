from cvm.datatypes.enums import DescriptiveIntEnum

class Currency(DescriptiveIntEnum):
    BRL = (1, 'Real')

class CurrencySize(DescriptiveIntEnum):
    UNIT     = (1, 'Unidade')
    THOUSAND = (2, 'Mil')