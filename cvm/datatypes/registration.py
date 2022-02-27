from cvm.datatypes.enums import DescriptiveIntEnum

class RegistrationCategory(DescriptiveIntEnum):
    A       = (1, 'Categoria A')
    B       = (2, 'Categoria B')
    UNKNOWN = (99, 'Não Identificado')

class RegistrationStatus(DescriptiveIntEnum):
    ACTIVE            = (1, 'Ativo')
    UNDER_EXAMINATION = (2, 'Em análise')
    NOT_GRANTED       = (3, 'Não concedido')
    SUSPENDED         = (4, 'Suspenso')
    CANCELED          = (5, 'Cancelada')