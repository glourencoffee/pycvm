from cvm.datatypes.enums import DescriptiveIntEnum

class Currency(DescriptiveIntEnum):
    BRL = (1, 'REAL')

class CurrencySize(DescriptiveIntEnum):
    UNIT     = (1, 'UNIDADE')
    THOUSAND = (2, 'MIL')