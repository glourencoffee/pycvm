import dataclasses
import datetime
import typing
from cvm import datatypes

# TODO: DFC_MD and DFC_MI should be removed,
#       as there is already a class for them (DFCMethod)
class StatementType(datatypes.DescriptiveIntEnum):
    BPA    = (1, 'Balanço Patrimonial Ativo')
    BPP    = (2, 'Balanço Patrimonial Passivo')
    DRE    = (3, 'Demonstração de Resultado')
    DRA    = (4, 'Demonstração de Resultado Abrangente')
    DFC    = (5, 'Demonstração de Fluxo de Caixa')
    DFC_MD = (6, 'Demonstração de Fluxo de Caixa (Método Direto)')
    DFC_MI = (7, 'Demonstração de Fluxo de Caixa (Método Indireto)')
    DMPL   = (8, 'Demonstração das Mutações do Patrimônio Líquido')
    DVA    = (9, 'Demonstração de Valor Adicionado')

class BalanceType(datatypes.DescriptiveIntEnum):
    INDIVIDUAL   = (0, 'Individual')
    CONSOLIDATED = (1, 'Consolidado')

class DFCMethod(datatypes.DescriptiveIntEnum):
    DIRECT   = (1, 'Método Direto')
    INDIRECT = (2, 'Método Indireto')

class FiscalYearOrder(datatypes.DescriptiveIntEnum):
    LAST           = (1, 'Último')
    SECOND_TO_LAST = (2, 'Penúltimo')

@dataclasses.dataclass(init=True, frozen=True)
class BPx:
    """This data structure is shared between the BPA and BPP statement types."""

    fiscal_year_end: datetime.date
    accounts: datatypes.AccountTuple

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
    accounts: datatypes.AccountTuple

@dataclasses.dataclass(init=True, frozen=True)
class DFC:
    """Cash Flow Statement ('Demonstração de Fluxo de Caixa' or 'DFC')    
    """

    method: DFCMethod
    fiscal_year_start: datetime.date
    fiscal_year_end: datetime.date
    accounts: datatypes.AccountTuple

@dataclasses.dataclass(init=True, frozen=True)
class DMPL:
    """Statement of Change in Net Equity ('Demonstração das Mutações do Patrimônio Líquido' or 'DMPL')"""

    fiscal_year_start: datetime.date
    fiscal_year_end: datetime.date
    columns: typing.Mapping[str, datatypes.AccountTuple]

StatementUnion = typing.Union[BPx, DRxDVA, DMPL, DFC]

class StatementCollection:
    """Groups all statements in one place.
    
    Companies are required to send three types of statements in their DFP/ITR,
    namely, the balance sheet, the income statement, and the cash flow statement.
    Article 25-A, paragragh 2 of Instruction 480/2009 states (Portuguese):

        "As demonstrações financeiras a serem entregues nos termos do inciso III do § 1º devem ser
        comparativas com as do exercício anterior e conter:
            I - balanço patrimonial;\n
            II – demonstração dos resultados;\n
            III – demonstração dos fluxos de caixa elaborada pelo método direto; e\n
            IV – notas explicativas."

    Note that Item IV is not present in DFP/ITR files, since DFP/ITR only
    contain financial statements.
    
    Although Item III of that Article says that companies should send their
    cash flow statements using the direct method, what happens in practice is
    that most companies use the indirect method, with very few companies using
    the direct method. Thus, this class requires the three kinds of statements
    upon construction, and the cash flow statement can be of any kind.
    """

    def __init__(self, statements: typing.Dict[StatementType, StatementUnion]) -> None:
        self._statements = {}

        try:
            for stmt_type in (StatementType.BPA, StatementType.BPP, StatementType.DRE, StatementType.DFC):
                self._statements[stmt_type] = statements[stmt_type]

        except KeyError as exc:
            stmt_type: StatementType = exc.args[0]

            raise KeyError(f'missing {stmt_type.name}') from None

        for stmt_type in (StatementType.DRA, StatementType.DMPL, StatementType.DVA):
            self._statements[stmt_type] = statements.get(stmt_type, None)

    @property
    def bpa(self) -> BPx:
        return self._statements[StatementType.BPA]

    @property
    def bpp(self) -> BPx:
        return self._statements[StatementType.BPP]

    @property
    def dre(self) -> DRxDVA:
        return self._statements[StatementType.DRE]

    @property
    def dra(self) -> typing.Optional[DRxDVA]:
        return self._statements[StatementType.DRA]

    @property
    def dmpl(self) -> typing.Optional[DMPL]:
        return self._statements[StatementType.DMPL]

    @property
    def dfc(self) -> typing.Optional[DFC]:
        return self._statements[StatementType.DFC]

    @property
    def dva(self) -> typing.Optional[DRxDVA]:
        return self._statements[StatementType.DVA]

    __slots__ = (
        '_statements'
    )