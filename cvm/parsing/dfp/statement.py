import enum
import collections
import csv
import logging
from datetime                 import date
from typing                   import Dict, List, DefaultDict
from cvm.datatypes.currency   import Currency, CurrencySize
from cvm.datatypes.statement  import StatementType, StatementMethod
from cvm.datatypes.cnpj       import CNPJ
from cvm.datatypes.enums      import DescriptiveIntEnum
from cvm.parsing.csvrow       import CsvRow
from cvm.parsing.util         import date_from_string
from cvm.parsing.exceptions   import ParseError, BadDocument
from cvm.parsing.dfp.account  import Account
from cvm.parsing.dfp.balance  import Balance
from cvm.parsing.dfp.element  import Element, ElementReader

class FiscalYearOrder(DescriptiveIntEnum):
    LAST           = (1, 'Último')
    SECOND_TO_LAST = (2, 'Penúltimo')

class Statement(Element):
    corporate_name: str
    cvm_code: int
    currency: Currency
    currency_size: CurrencySize
    fiscal_year_end: date

class BPStatement(Statement):
    accounts: Dict[FiscalYearOrder, List[Account]]

class DStatement(Statement):
    fiscal_year_start: date
    accounts: List[Account]

class DFCStatement(DStatement):
    method: StatementMethod

class DMPLStatement(Statement):
    fiscal_year_start: date
    accounts: Dict[str, Dict[FiscalYearOrder, List[Account]]]

class StatementCollection:
    """Groups all types of statements in one place.

    This class is meant to be used as a member of `Document`, such that access to can be
    performed by `Document.individual.bpa`, and so on.

    This class also aids the class `Document` by validating that all statements are
    present. A missing statement is considered a failure.

    A DFC statement in particular may be direct or indirect, so this class ensures that
    at least one is provided, which will be the one assigned to the property `dfc`.
    """

    __slots__ = [
        '_bpa',
        '_bpp',
        '_dre',
        '_dra',
        '_dfc',
        '_dmpl',
        '_dva'
    ]
    @property
    def bpa(self) -> BPStatement:
        return self._bpa

    @property
    def bpp(self) -> BPStatement:
        return self._bpp

    @property
    def dre(self) -> DStatement:
        return self._dre

    @property
    def dra(self) -> DStatement:
        return self._dra

    @property
    def dmpl(self) -> DMPLStatement:
        return self._dmpl

    @property
    def dfc(self) -> DFCStatement:
        return self._dfc

    @property
    def dva(self) -> DStatement:
        return self._dva

    def __init__(self, statements: Dict[StatementType, Statement]):
        try:
            self._bpa  = statements[StatementType.BPA]
            self._bpp  = statements[StatementType.BPP]
            self._dre  = statements[StatementType.DRE]
            self._dra  = statements[StatementType.DRA]
            self._dmpl = statements[StatementType.DMPL]
            self._dva  = statements[StatementType.DVA]
        except KeyError as exc:
            stmt_type: StatementType = exc.args[0]

            raise BadDocument(f'missing {stmt_type.name} statement') from None

        if StatementType.DFC_MD in statements:
            self._dfc = statements[StatementType.DFC_MD]
        else:
            try:
                self._dfc = statements[StatementType.DFC_MI]
            except KeyError:
                raise BadDocument('document has neither DFC-MD nor DFC-MI')

class StatementReader(ElementReader):
    __elemtype__ = Statement

    def read(self, elem: Statement, row: CsvRow):
        elem.corporate_name    = row.required('DENOM_CIA',    str)
        elem.cvm_code          = row.required('CD_CVM',       int)
        elem.currency          = row.required('MOEDA',        Currency)
        elem.currency_size     = row.required('ESCALA_MOEDA', CurrencySize)
        elem.fiscal_year_end   = row.required('DT_FIM_EXERC', date_from_string)

    def read_account(self, row: CsvRow) -> Account:
        acc = Account(
            code      = row.required('CD_CONTA',      str),
            name      = row.required('DS_CONTA',      str),
            quantity  = row.required('VL_CONTA',      float),
            is_fixed  = row.required('ST_CONTA_FIXA', str) == 'S'
        )
        
        return acc

class BPStatementReader(StatementReader):
    __elemtype__ = BPStatement

    def read(self, elem: BPStatement, row: CsvRow):
        super().read(elem, row)

        fiscal_year_order = row.required('ORDEM_EXERC', FiscalYearOrder)

        if not hasattr(elem, 'accounts'):
            elem.accounts = collections.defaultdict(list)

        elem.accounts[fiscal_year_order].append(self.read_account(row))

class DStatementReader(StatementReader):
    __elemtype__ = DStatement

    def read(self, elem: DStatement, row: CsvRow):
        super().read(elem, row)

        elem.fiscal_year_start = row.required('DT_INI_EXERC', date_from_string)
        fiscal_year_order      = row.required('ORDEM_EXERC',  FiscalYearOrder)
        
        if not hasattr(elem, 'accounts'):
            elem.accounts = collections.defaultdict(list)

        elem.accounts[fiscal_year_order].append(self.read_account(row))

class DFCStatementReader(DStatementReader):
    __elemtype__ = DFCStatement

    def read(self, elem: DFCStatement, row: CsvRow):
        super().read(elem, row)

        stmt_name = row.required('GRUPO_DFP', str)

        try:
            method_name = stmt_name.split('(')[1].rstrip(')')
        except IndexError:
            raise ParseError('GRUPO_DFP', stmt_name)

        elem.method = StatementMethod(method_name)

class DMPLStatementReader(StatementReader):
    __elemtype__ = DMPLStatement

    def read(self, elem: DMPLStatement, row: CsvRow):
        super().read(elem, row)

        elem.fiscal_year_start = row.required('DT_INI_EXERC', date_from_string)
        fiscal_year_order      = row.required('ORDEM_EXERC',  FiscalYearOrder)
        column                 = row.required('COLUNA_DF',    str)

        if not hasattr(elem, 'accounts'):
            elem.accounts = collections.defaultdict(lambda: collections.defaultdict(list))

        elem.accounts[fiscal_year_order][column].append(self.read_account(row))