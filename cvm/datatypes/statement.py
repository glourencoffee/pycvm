from __future__ import annotations
import dataclasses
import datetime
import typing
from cvm import datatypes

__all__ = [
    'StatementType',
    'BalanceType',
    'DFCMethod',
    'FiscalYearOrder',
    'Statement',
    'BPx',
    'DRxDVA',
    'DFC',
    'DMPL',
    'StatementCollection',
    'GroupedStatementCollection'
]

class StatementType(datatypes.DescriptiveIntEnum):
    BPA  = (1, 'Balanço Patrimonial Ativo')
    BPP  = (2, 'Balanço Patrimonial Passivo')
    DRE  = (3, 'Demonstração de Resultado')
    DRA  = (4, 'Demonstração de Resultado Abrangente')
    DFC  = (5, 'Demonstração de Fluxo de Caixa')
    DMPL = (6, 'Demonstração das Mutações do Patrimônio Líquido')
    DVA  = (7, 'Demonstração de Valor Adicionado')

class BalanceType(datatypes.DescriptiveIntEnum):
    INDIVIDUAL   = (0, 'Individual')
    CONSOLIDATED = (1, 'Consolidado')

class DFCMethod(datatypes.DescriptiveIntEnum):
    DIRECT   = (1, 'Método Direto')
    INDIRECT = (2, 'Método Indireto')

class FiscalYearOrder(datatypes.DescriptiveIntEnum):
    LAST           = (1, 'Último')
    SECOND_TO_LAST = (2, 'Penúltimo')

@dataclasses.dataclass(init=True)
class Statement:
    fiscal_year_order: FiscalYearOrder
    currency: datatypes.Currency
    currency_size: datatypes.CurrencySize
    accounts: typing.List[datatypes.BaseAccount]

    def normalized(self) -> Statement:
        """Returns a copy of `self` with `currency_size` as `CurrencySize.UNIT`."""

        if self.currency_size == datatypes.CurrencySize.UNIT:
            return dataclasses.replace(self)
        else:
            if self.currency_size != datatypes.CurrencySize.THOUSAND:
                raise ValueError(f"unknown currency size '{self.currency_size}'")
            
            normalized_accounts = []
            multiplier = 1000

            for account in self.accounts:
                normalized_accounts.append(self.normalize_account(account, multiplier))

            normalized_statement = dataclasses.replace(
                self,
                currency_size = datatypes.CurrencySize.UNIT,
                accounts      = normalized_accounts
            )

            return normalized_statement

    @staticmethod
    def normalize_account(account: datatypes.BaseAccount, multiplier: int) -> datatypes.BaseAccount:
        if isinstance(account, datatypes.Account):
            return dataclasses.replace(
                account,
                quantity = Statement.normalize_quantity(account.quantity, multiplier)
            )

        elif isinstance(account, datatypes.DMPLAccount):
            return dataclasses.replace(
                account,
                share_capital                       = Statement.normalize_quantity(account.share_capital,                       multiplier),
                capital_reserve_and_treasury_shares = Statement.normalize_quantity(account.capital_reserve_and_treasury_shares, multiplier),
                profit_reserves                     = Statement.normalize_quantity(account.profit_reserves,                     multiplier),
                unappropriated_retained_earnings    = Statement.normalize_quantity(account.unappropriated_retained_earnings,    multiplier),
                other_comprehensive_income          = Statement.normalize_quantity(account.other_comprehensive_income,          multiplier),
                controlling_interest                = Statement.normalize_quantity(account.controlling_interest,                multiplier),
                non_controlling_interest            = Statement.normalize_quantity(account.non_controlling_interest,            multiplier),
                consolidated_equity                 = Statement.normalize_quantity(account.consolidated_equity,                 multiplier),
            )

        else:
            raise ValueError(f'unknown account class: {account.__class__}')

    @staticmethod
    def normalize_quantity(quantity: typing.Optional[float], multiplier: int) -> typing.Optional[int]:
        if quantity is None:
            return None
        
        return round(quantity * multiplier)

@dataclasses.dataclass(init=True)
class BPx(Statement):
    """This data structure is shared between the BPA and BPP statement types."""

    accounts: typing.List[datatypes.Account]
    period_end_date: datetime.date

    def __repr__(self) -> str:
        return (
            '<BPx: '
                f'fiscal_year_order={self.fiscal_year_order.name} '
                f'period_end_date={self.period_end_date}'
            '>'
        )

@dataclasses.dataclass(init=True, repr=False)
class DRxDVA(Statement):
    """
    This class covers three statement types, namely:
    - Profit-and-loss Statement ('Demonstração de Resultado [de Exercício])' or 'DRE')
    - Profit-and-loss Overview Statement ('Demonstração de Resultado Abrangente' or 'DRA)
    - Statement of Value Added ('Demonstração de Valor Adicionado' or 'DVA')
    """

    accounts: typing.List[datatypes.Account]
    period_start_date: datetime.date
    period_end_date: datetime.date

    def __repr__(self) -> str:
        return (
            '<DRxDVA: '
                f'fiscal_year_order={self.fiscal_year_order.name} '
                f'period=({self.period_start_date}, {self.period_end_date})'
            '>'
        )

@dataclasses.dataclass(init=True)
class DFC(Statement):
    """Cash Flow Statement ('Demonstração de Fluxo de Caixa' or 'DFC')    
    """

    accounts: typing.List[datatypes.Account]
    method: DFCMethod
    period_start_date: datetime.date
    period_end_date: datetime.date
    
    def __repr__(self) -> str:
        return (
            '<DFC: '
                f'fiscal_year_order={self.fiscal_year_order.name} '
                f'period=({self.period_start_date}, {self.period_end_date}) '
                f'method={self.method.name}'
            '>'
        )

@dataclasses.dataclass(init=True)
class DMPL(Statement):
    """Statement of Changes in Net Equity ('Demonstração das Mutações do Patrimônio Líquido' or 'DMPL')"""

    accounts: typing.List[datatypes.DMPLAccount]
    period_start_date: datetime.date
    period_end_date: datetime.date

    def __repr__(self) -> str:
        return (
            '<DMPL: '
                f'fiscal_year_order={self.fiscal_year_order.name} '
                f'period=({self.period_start_date}, {self.period_end_date}) '
                f'accounts={len(self.accounts)}'
            '>'
        )

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

    def __init__(self,
                 balance_type: BalanceType,
                 statements_by_type: typing.Dict[StatementType, Statement],
                 extra_dre: typing.Optional[DRxDVA],
                 extra_dra: typing.Optional[DRxDVA]
    ) -> None:
        self._balance_type = balance_type
        self._statements = {}

        try:
            for stmt_type in (StatementType.BPA, StatementType.BPP, StatementType.DRE, StatementType.DFC):
                self._statements[stmt_type] = statements_by_type[stmt_type]

        except KeyError as exc:
            stmt_type: StatementType = exc.args[0]

            raise KeyError(f'missing {stmt_type.name}') from None

        for stmt_type in (StatementType.DRA, StatementType.DMPL, StatementType.DVA):
            self._statements[stmt_type] = statements_by_type.get(stmt_type, None)

        self._extra_dre = extra_dre
        self._extra_dra = extra_dra

    @property
    def balance_type(self) -> BalanceType:
        return self._balance_type

    @property
    def bpa(self) -> BPx:
        return self.statement(StatementType.BPA)

    @property
    def bpp(self) -> BPx:
        return self.statement(StatementType.BPP)

    @property
    def dre(self) -> DRxDVA:
        return self.statement(StatementType.DRE)

    @property
    def dra(self) -> typing.Optional[DRxDVA]:
        return self.statement(StatementType.DRA)

    @property
    def dmpl(self) -> typing.Optional[DMPL]:
        return self.statement(StatementType.DMPL)

    @property
    def dfc(self) -> DFC:
        return self.statement(StatementType.DFC)

    @property
    def dva(self) -> typing.Optional[DRxDVA]:
        return self.statement(StatementType.DVA)

    @property
    def extra_dre(self) -> typing.Optional[DRxDVA]:
        return self._extra_dre

    @property
    def extra_dra(self) -> typing.Optional[DRxDVA]:
        return self._extra_dra

    def statement(self, statement_type: StatementType) -> typing.Optional[Statement]:
        return self._statements[statement_type]

    def __getitem__(self, statement_type: StatementType) -> typing.Optional[Statement]:
        return self._statements[statement_type]

    __slots__ = (
        '_balance_type',
        '_statements',
        '_extra_dre',
        '_extra_dra'
    )

    def __repr__(self) -> str:
        s = ''

        for attr_name in 'bpa bpp dre dra dmpl dfc dva extra_dre extra_dra'.split():
            stmt      = getattr(self, attr_name)
            yes_or_no = 'yes' if stmt is not None else 'no'

            s += f'{attr_name}={yes_or_no} '

        return f'<StatementCollection: balance_type={self.balance_type.name} {s.rstrip()}>'

class GroupedStatementCollection:
    """Groups `Statement` by `FiscalYearOrder`.

    This class separates statements by the fiscal year they were delivered,
    while providing a short-and-simple syntax for accessing the two types of
    fiscal year order, the last fiscal year and the previous fiscal year, by
    the properties `last` and `previous`, respectively.
    """

    __slots__= ('_prev', '_last')

    def __init__(self,
                 balance_type: BalanceType,
                 statements_by_type: typing.Dict[StatementType, typing.List[Statement]]
    ) -> None:
        last_fy_stmts  = {}
        prev_fy_stmts  = {}
        last_dre_extra = None
        last_dra_extra = None
        prev_dre_extra = None
        prev_dra_extra = None

        def is_extra_drx(stmt: DRxDVA):
            # ITR documents may have more than one DRE/DRA statement for
            # each fiscal year order. For example, the ITR for the second
            # quarter of a year may have 4 DRE statements, one for the
            # second quarter and another for the first semester, for each
            # fiscal year order, thus resulting in a total of 4 statements:
            #   - 2010-04-01 to 2010-06-30 (last fiscal year, second quarter)
            #   - 2010-01-01 to 2010-06-30 (last fiscal year, first semester)
            #   - 2009-04-01 to 2009-06-30 (previous fiscal year, second quarter)
            #   - 2009-01-01 to 2009-06-30 (previous fiscal year, first semester)
            #
            # We check for `days < 360` so that we don't mistakenly
            # consider a DRE/DRA coming from a DFP document as "extra".
            #
            # Note that this doesn't apply to DVA documents, as they
            # normally cover up a period that is more than a quarter.
            # For example, a DVA from 2010-01-01 to 2010-06-30 is just
            # a normal DVA, not an "extra". Hence why this function is
            # called "is_extra_drx()" rather than "is_extra_drx_dva()".

            days = (stmt.period_end_date - stmt.period_start_date).days

            return days > 91 and days < 360

        for stmt_type, stmts in statements_by_type.items():
            is_dre = (stmt_type == StatementType.DRE)
            is_dra = (stmt_type == StatementType.DRA)

            for stmt in stmts:
                if stmt.fiscal_year_order == FiscalYearOrder.LAST:
                    if is_dre and last_dre_extra is None and is_extra_drx(stmt):
                        last_dre_extra = stmt

                    elif is_dra and last_dra_extra is None and is_extra_drx(stmt):
                        last_dra_extra = stmt

                    elif stmt_type not in last_fy_stmts:
                        last_fy_stmts[stmt_type] = stmt

                    else:
                        print('unknown extra (last) statement of type ', stmt_type, ': ', stmt, sep='')

                elif stmt.fiscal_year_order == FiscalYearOrder.SECOND_TO_LAST:
                    if is_dre and prev_dre_extra is None and is_extra_drx(stmt):
                        prev_dre_extra = stmt

                    elif is_dra and prev_dra_extra is None and is_extra_drx(stmt):
                        prev_dra_extra = stmt

                    elif stmt_type not in prev_fy_stmts:
                        prev_fy_stmts[stmt_type] = stmt

                    else:
                        print('unknown extra (previous) statement of type ', stmt_type, ': ', stmt, sep='')

        self._last = StatementCollection(balance_type, last_fy_stmts, last_dre_extra, last_dra_extra)
        self._prev = StatementCollection(balance_type, prev_fy_stmts, prev_dre_extra, prev_dra_extra)

    @property
    def previous(self) -> StatementCollection:
        return self._prev

    @property
    def last(self) -> StatementCollection:
        return self._last

    def collections(self) -> typing.Tuple[StatementCollection, StatementCollection]:
        return (self._prev, self._last)

    def collection(self, fiscal_year_order: FiscalYearOrder) -> StatementCollection:
        if fiscal_year_order == FiscalYearOrder.LAST:
            return self._last
        elif fiscal_year_order == FiscalYearOrder.SECOND_TO_LAST:
            return self._prev
        else:
            raise ValueError(f'invalid fiscal year order {fiscal_year_order}')

    def __getitem__(self, fiscal_year_order: FiscalYearOrder) -> StatementCollection:
        return self.collection(fiscal_year_order)