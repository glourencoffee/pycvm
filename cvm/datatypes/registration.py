from cvm import datatypes

class RegistrationCategory(datatypes.DescriptiveIntEnum):
    A       = (1, 'Categoria A')
    B       = (2, 'Categoria B')
    UNKNOWN = (99, 'Não Identificado')

class RegistrationStatus(datatypes.DescriptiveIntEnum):
    ACTIVE         = (1, 'Ativo')
    UNDER_ANALYSIS = (2, 'Em análise')
    NOT_GRANTED    = (3, 'Não concedido')
    SUSPENDED      = (4, 'Suspenso')
    CANCELED       = (5, 'Cancelada')