import dataclasses
import datetime
import typing
from cvm.datatypes.account  import Account, AccountTuple
from cvm.datatypes.currency import Currency, CurrencySize
from cvm.datatypes.enums    import DescriptiveIntEnum

class StatementType(DescriptiveIntEnum):
    BPA    = (1, 'Balanço Patrimonial Ativo')
    BPP    = (2, 'Balanço Patrimonial Passivo')
    DRE    = (3, 'Demonstração de Resultado')
    DRA    = (4, 'Demonstração de Resultado Abrangente')
    DFC_MD = (5, 'Demonstração de Fluxo de Caixa (Método Direto)')
    DFC_MI = (6, 'Demonstração de Fluxo de Caixa (Método Indireto)')
    DMPL   = (7, 'Demonstração das Mutações do Patrimônio Líquido')
    DVA    = (8, 'Demonstração de Valor Adicionado')

class DFCMethod(DescriptiveIntEnum):
    DIRECT   = (1, 'Método Direto')
    INDIRECT = (2, 'Método Indireto')

class FiscalYearOrder(DescriptiveIntEnum):
    LAST           = (1, 'Último')
    SECOND_TO_LAST = (2, 'Penúltimo')

@dataclasses.dataclass(init=True, frozen=True)
class BPx:
    """This data structure is shared between the BPA and BPP statement types."""

    fiscal_year_end: datetime.date
    accounts: AccountTuple

@dataclasses.dataclass(init=True, frozen=True)
class DRxDVA:
    """
    This class covers three statement types, namely:
    - Profit-and-loss Statement ('Demonstração de Resultado [de Exercício])' or 'DRE')
    - Profit-and-loss Overview Statement ('Demonstração de Resultado Abrangente' or 'DRA)
    - Statement of Value Added ('Demonstração de Valor Adicionado' or 'DVA')
    """

    fiscal_year_start: datetime.date
    fiscal_year_end: datetime.date
    accounts: AccountTuple

@dataclasses.dataclass(init=True, frozen=True)
class DFC:
    """Cash Flow Statement ('Demonstração de Fluxo de Caixa' or 'DFC')    
    """

    method: DFCMethod
    fiscal_year_start: datetime.date
    fiscal_year_end: datetime.date
    accounts: AccountTuple

@dataclasses.dataclass(init=True, frozen=True)
class DMPL:
    """Statement of Change in Net Equity ('Demonstração das Mutações do Patrimônio Líquido' or 'DMPL')"""

    fiscal_year_start: datetime.date
    fiscal_year_end: datetime.date
    columns: typing.Mapping[str, AccountTuple]

@dataclasses.dataclass(init=True, frozen=True)
class StatementCollection:
    """Groups all types of statements in one place."""

    bpa: BPx
    bpp: BPx
    dre: DRxDVA
    dra: DRxDVA
    dmpl: DMPL
    dfc: DFC
    dva: DRxDVA

    __slots__ = [
        'bpa',
        'bpp',
        'dre',
        'dra',
        'dmpl',
        'dfc',
        'dva'
    ]
