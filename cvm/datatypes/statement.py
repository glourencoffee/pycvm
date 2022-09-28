from __future__ import annotations
import dataclasses
import datetime
import typing
from enum import IntEnum, auto
from cvm  import datatypes

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

class StatementType(IntEnum):
    BPA  = auto() # 'Balanço Patrimonial Ativo'
    BPP  = auto() # 'Balanço Patrimonial Passivo'
    DRE  = auto() # 'Demonstração de Resultado'
    DRA  = auto() # 'Demonstração de Resultado Abrangente'
    DFC  = auto() # 'Demonstração de Fluxo de Caixa'
    DMPL = auto() # 'Demonstração das Mutações do Patrimônio Líquido'
    DVA  = auto() # 'Demonstração de Valor Adicionado'

class BalanceType(IntEnum):
    INDIVIDUAL   = auto() # 'Individual'
    CONSOLIDATED = auto() # 'Consolidado'

class DFCMethod(IntEnum):
    DIRECT   = auto() # 'Método Direto'
    INDIRECT = auto() # 'Método Indireto'

class FiscalYearOrder(IntEnum):
    LAST           = auto() # 'Último'
    SECOND_TO_LAST = auto() # 'Penúltimo'

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

    Although the above holds true for most documents, income and cash flow
    statements are sometimes not given. One reason for that is having no
    financial movements in a period. This is why the properties `dre` and
    `dfc` are optional.

    Likewise, the balance sheet is mostly present, but there are also
    cases when either a BPA or BPP is not given. One reason for that
    is a company that has just started its business activities and has
    no balances for the last fiscal year. For example, if a company was
    created in the year of 2016, it will have no balance sheet for 2015,
    since there was no activity in 2015, but it may still provide a BPA
    or BPP. In case it provides a BPA or BPP, it is often filled with zero
    balances.

    Note that Item IV is not present in DFP/ITR files, since DFP/ITR only
    contain financial statements.
    
    Also note that although Item III of that Article says that companies
    should send their cash flow statements using the direct method, what
    happens in practice is that most companies use the indirect method,
    with very few companies using the direct method. Thus, the cash flow
    statement can be of any kind.
    """

    def __init__(self,
                 balance_type: BalanceType,
                 statements: typing.Dict[StatementType, Statement],
                 extra_dre: typing.Optional[DRxDVA],
                 extra_dra: typing.Optional[DRxDVA]
    ) -> None:
        self._balance_type = balance_type
        self._statements = {}

        try:
            for stmt_type in (StatementType.BPA, StatementType.BPP):
                self._statements[stmt_type] = statements[stmt_type]

        except KeyError as exc:
            stmt_type: StatementType = exc.args[0]

            # 'missing (individual|consolidated) (BPA|BPP)'
            raise KeyError(f'missing {balance_type.name.lower()} {stmt_type.name}') from None

        for stmt_type in (StatementType.DRE, StatementType.DRA, StatementType.DFC, StatementType.DMPL, StatementType.DVA):
            self._statements[stmt_type] = statements.get(stmt_type, None)

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
    def dre(self) -> typing.Optional[DRxDVA]:
        return self.statement(StatementType.DRE)

    @property
    def dra(self) -> typing.Optional[DRxDVA]:
        return self.statement(StatementType.DRA)

    @property
    def dmpl(self) -> typing.Optional[DMPL]:
        return self.statement(StatementType.DMPL)

    @property
    def dfc(self) -> typing.Optional[DFC]:
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

    Note that some `DFPITR` documents only have statements for the last fiscal
    year, while some other have it for both the last and previous fiscal years.
    For example, it happens in the DFP of 2010 to have companies with statements
    of 2010 (`last`) as well as 2009 (`previous`), but it also has companies with
    statements only of 2010, in which case `previous` is None.
    """

    __slots__= ('_prev', '_last')

    @staticmethod
    def from_dfp_statements(balance_type: BalanceType, 
                            statements: typing.Dict[StatementType, typing.List[Statement]]
    ) -> GroupedStatementCollection:

        def is_extra_drx(stmt: DRxDVA):
            # Unlike ITR documents, DFP documents don't have extra DRE/DRA
            # statements for each fiscal year order, so this function always
            # returns False.
            # 
            # What may happen, however, is that DRE statements coming from a
            # DFP may have a period smaller than one year. For example, in the
            # DFP of 2010, the individual DRE by company "SAAG INVESTIMENTOS S.A."
            # goes from 2010-02-25 to 2010-12-31. It is a DRE that only has
            # accounts for the last fiscal year, thus making `previous` a None.
            #
            # Another example from the same DFP is the individual DRE by
            # company "BERNA PARTICIPAÇÕES SA", which goes from 2010-01-01
            # to 2010-12-31 for the last fiscal year, but whose balances
            # for the previous fiscal year goes from 2009-09-01 to 2009-12-31.
            # In other words, this DRE reports balances for the last quarter
            # of the previous year, rather than balances for the whole previous
            # year.
            #
            # The conclusion is that not every DRE from a DFP will have a date
            # range from 01 January to 31 December, be it for the last fiscal
            # year or for the previous fiscal year. Fortunately, though, no
            # more than two DRE statements are found in a DFP document.

            return False

        return GroupedStatementCollection._from_statements(balance_type, statements, extra_drx_checker=is_extra_drx)

    @staticmethod
    def from_itr_statements(balance_type: BalanceType,
                            statements: typing.Dict[StatementType, typing.List[Statement]]
    ) -> GroupedStatementCollection:

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
            # Note that this doesn't apply to DVA documents, as they
            # normally cover up a period that is more than a quarter.
            # For example, a DVA from 2010-01-01 to 2010-06-30 is just
            # a normal DVA, not an "extra". Hence why this function is
            # called "is_extra_drx()" rather than "is_extra_drx_dva()".

            days = (stmt.period_end_date - stmt.period_start_date).days

            return days > 91

        return GroupedStatementCollection._from_statements(balance_type, statements, extra_drx_checker=is_extra_drx)

    @staticmethod
    def _from_statements(balance_type: BalanceType,
                         statements: typing.Dict[StatementType, typing.List[Statement]],
                         extra_drx_checker: typing.Callable[[DRxDVA], bool]
    ) -> GroupedStatementCollection:

        last_fy_stmts  = {}
        prev_fy_stmts  = {}
        last_dre_extra = None
        last_dra_extra = None
        prev_dre_extra = None
        prev_dra_extra = None

        for stmt_type, stmts in statements.items():
            is_dre = (stmt_type == StatementType.DRE)
            is_dra = (stmt_type == StatementType.DRA)

            for stmt in stmts:
                if stmt.fiscal_year_order == FiscalYearOrder.LAST:
                    if is_dre and last_dre_extra is None and extra_drx_checker(stmt):
                        last_dre_extra = stmt

                    elif is_dra and last_dra_extra is None and extra_drx_checker(stmt):
                        last_dra_extra = stmt

                    elif stmt_type not in last_fy_stmts:
                        last_fy_stmts[stmt_type] = stmt

                    else:
                        print('Ignoring unknown extra (last) statement of type ', stmt_type.name, ': ', stmt, sep='')

                elif stmt.fiscal_year_order == FiscalYearOrder.SECOND_TO_LAST:
                    if is_dre and prev_dre_extra is None and extra_drx_checker(stmt):
                        prev_dre_extra = stmt

                    elif is_dra and prev_dra_extra is None and extra_drx_checker(stmt):
                        prev_dra_extra = stmt

                    elif stmt_type not in prev_fy_stmts:
                        prev_fy_stmts[stmt_type] = stmt

                    else:
                        print('Ignoring unknown extra (previous) statement of type ', stmt_type.name, ': ', stmt, sep='')

        last = StatementCollection(balance_type, last_fy_stmts, last_dre_extra, last_dra_extra)

        if len(prev_fy_stmts) > 0:
            prev = StatementCollection(balance_type, prev_fy_stmts, prev_dre_extra, prev_dra_extra)
        else:
            prev = None

        return GroupedStatementCollection(last=last, previous=prev)

    def __init__(self, last: StatementCollection, previous: typing.Optional[StatementCollection]) -> None:
        self._last = last
        self._prev = previous

    @property
    def previous(self) -> typing.Optional[StatementCollection]:
        return self._prev

    @property
    def last(self) -> StatementCollection:
        return self._last

    def collections(self) -> typing.Tuple[StatementCollection]:
        if self._prev is not None:
            return (self._prev, self._last)
        else:
            return (self._last,)

    def collection(self, fiscal_year_order: FiscalYearOrder) -> typing.Optional[StatementCollection]:
        if fiscal_year_order == FiscalYearOrder.LAST:
            return self._last
        elif fiscal_year_order == FiscalYearOrder.SECOND_TO_LAST:
            return self._prev
        else:
            raise ValueError(f'invalid fiscal year order {fiscal_year_order}')

    def __getitem__(self, fiscal_year_order: FiscalYearOrder) -> typing.Optional[StatementCollection]:
        return self.collection(fiscal_year_order)