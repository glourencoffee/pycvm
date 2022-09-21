from cvm import datatypes

__all__ = [
    'FederatedState'
]

class FederatedState(datatypes.DescriptiveIntEnum):
    """Enumerates all of the 27 Federate States of Brazil."""
    
    AC = (1,  'Acre')
    AL = (2,  'Alagoas')
    AP = (3,  'Amapá')
    AM = (4,  'Amazonas')
    BA = (5,  'Bahia')
    CE = (6,  'Ceará')
    DF = (7,  'Distrito Federal')
    GO = (8,  'Goiás')
    ES = (9,  'Espírito Santo')
    MA = (10, 'Maranhão')
    MT = (11, 'Mato Grosso')
    MS = (12, 'Mato Grosso do Sul')
    MG = (13, 'Minas Gerais')
    PA = (14, 'Pará')
    PB = (15, 'Paraiba')
    PR = (16, 'Paraná')
    PE = (17, 'Pernambuco')
    PI = (18, 'Piauí')
    RJ = (19, 'Rio de Janeiro')
    RN = (20, 'Rio Grande do Norte')
    RS = (21, 'Rio Grande do Sul')
    RO = (22, 'Rondônia')
    RR = (23, 'Rorâima')
    SP = (24, 'São Paulo')
    SC = (25, 'Santa Catarina')
    SE = (26, 'Sergipe')
    TO = (27, 'Tocantins')