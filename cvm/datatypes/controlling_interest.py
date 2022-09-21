from cvm import datatypes

__all__ = [
    'ControllingInterest'
]

class ControllingInterest(datatypes.DescriptiveIntEnum):
    GOVERNMENTAL         = (1, 'Estatal')
    GOVERNMENTAL_HOLDING = (2, 'Estatal Holding')
    FOREIGN              = (3, 'Estrangeiro')
    FOREIGN_HOLDING      = (4, 'Estrangeiro Holding')
    PRIVATE              = (5, 'Privado')
    PRIVATE_HOLDING      = (6, 'Privado Holding')