from cvm.datatypes.enums import DescriptiveIntEnum

class StatementType(DescriptiveIntEnum):
    IF     = (1, 'Informação Financeira')
    BPA    = (2, 'Balanço Patrimonial Ativo')
    BPP    = (3, 'Balanço Patrimonial Passivo')
    DRE    = (4, 'Demonstração de Resultado')
    DRA    = (5, 'Demonstração de Resultado Abrangente')
    DFC_MD = (6, 'Demonstração de Fluxo de Caixa (Método Direto)')
    DFC_MI = (7, 'Demonstração de Fluxo de Caixa (Método Indireto)')
    DMPL   = (8, 'Demonstração das Mutações do Patrimônio Líquido')
    DVA    = (9, 'Demonstração de Valor Adicionado')

class StatementMethod(DescriptiveIntEnum):
    DIRECT   = (1, 'Método Direto')
    INDIRECT = (2, 'Método Indireto')