import enum
import collections
import datetime
import csv
import logging
from typing                  import Optional, Generator, Tuple, Dict, List, Iterable
from cvm.datatypes.statement import StatementType
from cvm.parsing.util        import normalize_currency, normalize_quantity, date_from_string
from cvm.parsing.dfp.account import Account
from cvm.parsing.dfp.balance import Balance
from cvm.parsing.dfp         import bpa, dre

class Company:
    cnpj: str
    corporate_name: str
    cvm_code: str

    def __str__(self) -> str:
        return f'Company({ self.corporate_name } / CNPJ: { self.cnpj } / CVM: { self.cvm_code })'

class FiscalYearOrder(enum.Enum):
    LAST           = 'ÚLTIMO'
    SECOND_TO_LAST = 'PENÚLTIMO'

class Statement:
    version: int
    type: StatementType
    consolidated: bool
    company: Company
    currency: str
    accounts: list[Account]
    reference_date: datetime.date
    fiscal_year_start: Optional[datetime.date]
    fiscal_year_end: datetime.date
    fiscal_year_order: FiscalYearOrder

    def balance(self) -> Balance:
        if self.type == StatementType.BPA:
            return self._parse_balance(cls_list=(bpa.FinancialCompanyBalance, bpa.IndustrialCompanyBalance, bpa.InsuranceCompanyBalance))
        elif self.type == StatementType.DRE:
            return self._parse_balance(cls_list=(dre.IndustrialCompanyBalance,))

    def _parse_balance(self, cls_list) -> Balance:
        accounts_iter = iter(self.accounts)

        for cls in cls_list:
            try:
                return cls(accounts_iter)
            except ValueError:
                pass

        # TODO: specialize exception?
        raise ValueError('invalid/unknown balance layout')

class _RawStatement:
    __slots__ = [
        'reference_date',
        'version',
        'group',
        'cnpj',
        'corporate_name',
        'cvm_code',
        'currency_name',
        'currency_size',
        'fiscal_year_start',
        'fiscal_year_end',
        'fiscal_year_order',
        'accounts'
    ]

    reference_date: str
    version: str
    group: str
    cnpj: str
    corporate_name: str
    cvm_code: str
    currency_name: str
    currency_size: str
    fiscal_year_start: str
    fiscal_year_end: str
    fiscal_year_order: str
    accounts: List[Tuple[str, str, str, str]]

_stmt_groups_by_name = {
    'DF Consolidado - Balanço Patrimonial Ativo':                        (StatementType.BPA,    True),
    'DF Individual - Balanço Patrimonial Ativo':                         (StatementType.BPA,    False),
    'DF Consolidado - Balanço Patrimonial Passivo':                      (StatementType.BPP,    True),
    'DF Individual - Balanço Patrimonial Passivo':                       (StatementType.BPP,    False),
    'DF Consolidado - Demonstração do Resultado':                        (StatementType.DRE,    True),
    'DF Individual - Demonstração do Resultado':                         (StatementType.DRE,    False),
    'DF Consolidado - Demonstração de Resultado Abrangente':             (StatementType.DRA,    True),
    'DF Individual - Demonstração de Resultado Abrangente':              (StatementType.DRA,    False),
    'DF Consolidado - Demonstração do Fluxo de Caixa (Método Direto)':   (StatementType.DFC_MD, True),
    'DF Individual - Demonstração do Fluxo de Caixa (Método Direto)':    (StatementType.DFC_MD, False),
    'DF Consolidado - Demonstração do Fluxo de Caixa (Método Indireto)': (StatementType.DFC_MI, True),
    'DF Individual - Demonstração do Fluxo de Caixa (Método Indireto)':  (StatementType.DFC_MI, False),
    'DF Consolidado - Demonstração das Mutações do Patrimônio Líquido':  (StatementType.DMPL,   True),
    'DF Individual - Demonstração das Mutações do Patrimônio Líquido':   (StatementType.DMPL,   False),
    'DF Consolidado - Demonstração de Valor Adicionado':                 (StatementType.DVA,    True),
    'DF Individual - Demonstração de Valor Adicionado':                  (StatementType.DVA,    False)
}

def _read_statement_group(group: str) -> Tuple[StatementType, bool]:
    try:
        return _stmt_groups_by_name[group]
    except KeyError:
        raise ValueError(f"unknown DFP group '{ group }'") from None

def _read_raw_statements(csv_file, delimiter: str) -> Iterable[_RawStatement]:
    """Reads and returns DFP stmts as an iterable of `_RawStatement`s."""

    csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

    stmts = {}
    prev_row = ''

    for row_index, row in enumerate(csv_reader):
        # Clean up duplicate rows. I don't know why, but some rows are duplicated.
        if row == prev_row:
            continue

        prev_row = row

        try:
            cvm_code        = row['CD_CVM']
            reference_date  = row['DT_REFER']
            fiscal_year_end = row['DT_FIM_EXERC']
        except KeyError as e:
            logging.warn('failed to read row %d: %s', row_index, e)
            continue

        stmt_key = cvm_code + reference_date + fiscal_year_end

        try:
            stmt = stmts[stmt_key]
        except KeyError:
            stmt = _RawStatement()

            try:
                stmt.version           = row['VERSAO']
                stmt.group             = row['GRUPO_DFP']
                stmt.cnpj              = row['CNPJ_CIA']
                stmt.corporate_name    = row['DENOM_CIA']
                stmt.currency_name     = row['MOEDA']
                stmt.currency_size     = row['ESCALA_MOEDA']
                stmt.fiscal_year_start = row['DT_INI_EXERC'] if 'DT_INI_EXERC' in row else ''
                stmt.fiscal_year_order = row['ORDEM_EXERC']
            except KeyError as e:
                logging.warn('failed to read row %d: %s', row_index, e)
                continue

            stmt.cvm_code        = cvm_code
            stmt.reference_date  = reference_date
            stmt.fiscal_year_end = fiscal_year_end
            stmt.accounts        = []

            stmts[stmt_key] = stmt
                
        stmt.accounts.append((row['CD_CONTA'], row['DS_CONTA'], row['VL_CONTA'], row['ST_CONTA_FIXA']))

    return stmts.values()

def reader(csv_file, delimiter: str = ';') -> Generator[Statement, None, None]:
    """Returns a generator that reads a DFP stmt from a CSV file."""

    for raw_stmt in _read_raw_statements(csv_file, delimiter):
        try:
            r = Statement()
            r.version                = int(raw_stmt.version)
            r.type, r.consolidated   = _read_statement_group(raw_stmt.group)
            r.company                = Company()
            r.company.cnpj           = raw_stmt.cnpj
            r.company.corporate_name = raw_stmt.corporate_name
            r.company.cvm_code       = raw_stmt.cvm_code
            r.currency               = normalize_currency(raw_stmt.currency_name)
            r.reference_date         = date_from_string(raw_stmt.reference_date)
            r.fiscal_year_start      = date_from_string(raw_stmt.fiscal_year_start) if raw_stmt.fiscal_year_start != '' else None
            r.fiscal_year_end        = date_from_string(raw_stmt.fiscal_year_end)
            r.fiscal_year_order      = FiscalYearOrder(raw_stmt.fiscal_year_order)
            r.accounts               = []

            for code, name, quantity, is_fixed in raw_stmt.accounts:
                acc = Account()
                acc.code     = code
                acc.name     = name
                acc.quantity = normalize_quantity(float(quantity), raw_stmt.currency_size)
                acc.is_fixed = is_fixed == 'S'

                r.accounts.append(acc)
        except ValueError as exc:
            logging.warn(
                'failed to parse stmt of company %s (CVM: %s, fiscal year end: %s): %s',
                raw_stmt.corporate_name,
                raw_stmt.cvm_code,
                raw_stmt.fiscal_year_end,
                exc
            )

        yield r