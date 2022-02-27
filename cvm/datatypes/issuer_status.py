from cvm.datatypes.enums import DescriptiveIntEnum

class IssuerStatus(DescriptiveIntEnum):
    PRE_OPERATIONAL_PHASE           = (1, 'Fase Pré-Operacional')
    OPERATIONAL_PHASE               = (2, 'Fase Operacional')
    BANKRUPT                        = (4, 'Em Falência')
    EXTRAJUDICIAL_LIQUIDATION       = (5, 'Em Liquidação Extrajudicial')
    STALLED                         = (6, 'Paralisada')
    JUDICIAL_LIQUIDATION            = (7, 'Em Liquidação Judicial')
    JUDICIAL_RECOVERY_OR_EQUIVALENT = (8, 'Em Recuperação Judicial ou Equivalente')
    EXTRAJUDICIAL_RECOVERY          = (9, 'Em Recuperação Extrajudicial')