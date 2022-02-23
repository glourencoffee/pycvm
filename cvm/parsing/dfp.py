import enum
import collections
import datetime
import csv
import logging
from typing                import Optional, Generator, Tuple, Dict, List, Iterable
from cvm.parsing.normalize import normalize_currency, normalize_quantity

class Company:
    cnpj: str
    corporate_name: str
    cvm_code: str

    def __str__(self) -> str:
        return f'Company({ self.corporate_name } / CNPJ: { self.cnpj } / CVM: { self.cvm_code })'

class ReportGroup(enum.Flag):
    BPA    = 1 # Balanço Patrimonial Ativo
    BPP    = 2 # Balanço Patrimonial Passivo
    DRE    = 3 # Demonstração de Resultado
    DRA    = 4 # Demonstração de Resultado Abrangente
    DMPL   = 5 # Demonstração das Mutações do Patrimônio Líquido
    # FIXME: disambiguate between MD and MI
    DFC_MD = 6 # Demonstração de Fluxo de Caixa (Método Direto)
    DFC_MI = 6 # Demonstração de Fluxo de Caixa (Método Indireto)
    DVA    = 7 # Demonstração de Valor Adicionado

class Account:
    code: str
    name: str
    quantity: float
    is_fixed: bool

    @property
    def level(self) -> int:
        return self.code.count('.') + 1

    def group(self) -> ReportGroup:
        sep_index = self.code.find('.')

        if sep_index == -1:
            root_level = int(self.code)
        else:
            root_level = int(self.code[:sep_index])

        return ReportGroup(root_level)

    def __str__(self) -> str:
        return f'Account({ self.code }, { self.name }, { self.quantity }, fixed: { self.is_fixed })'

class FiscalYearOrder(enum.Enum):
    LAST           = 'ÚLTIMO'
    SECOND_TO_LAST = 'PENÚLTIMO'

class Report:
    version: int
    group: ReportGroup
    consolidated: bool
    company: Company
    currency: str
    accounts: list[Account]
    reference_date: datetime.date
    fiscal_year_start: Optional[datetime.date]
    fiscal_year_end: datetime.date
    fiscal_year_order: FiscalYearOrder

class BalanceType(enum.Enum):
    # BPA balances
    CURRENT_ASSETS                 = enum.auto() # Ativo Circulante
    CASH_AND_CASH_EQUIVALENTS      = enum.auto() # Caixa e Equivalentes de Caixa (CCE)
    LIQUID_ASSETS                  = enum.auto() # Disponibilidades
    FINANCIAL_INVESTMENTS          = enum.auto() # Aplicações Financeiras
    ACCOUNTS_RECEIVABLE            = enum.auto() # Contas a Receber
    INVENTORIES                    = enum.auto() # Estoque
    NONCURRENT_ASSETS              = enum.auto() # Ativo Não Circulante
    LONG_TERM_ASSETS               = enum.auto() # Ativo Realizável a Longo Prazo
    LONG_TERM_INVESTIMENTS         = enum.auto() # Investimentos a Longo Prazo
    FIXED_ASSETS                   = enum.auto() # Ativo Imobilizado
    INTANGIBLE_ASSETS              = enum.auto() # Ativo Intangível

    # BPP balances
    # TODO

    # DRE balances
    NET_INCOME                     = enum.auto() # Receita Líquida
    COST_OF_GOODS_SOLD             = enum.auto() # Custos das Mercadorias Vendidas (COGS)
    GROSS_PROFIT                   = enum.auto() # Lucro Bruto
    OPERATING_REVENUE_AND_EXPENSES = enum.auto() # Receitas e Despesas Operacionais
    OPERATING_RESULT               = enum.auto() # Resultado Operacional (EBITDA)
    DEPRECIATION_AND_AMORTIZATION  = enum.auto() # Depreciação e Amortização
    OPERATING_PROFIT               = enum.auto() # Lucro Operacional (EBIT)
    FINANCIAL_RESULT               = enum.auto() # Resultado Financeiro
    EARNINGS_BEFORE_TAX            = enum.auto() # Resultado Antes dos Tributos sobre o Lucro (EBT)
    TAX_EXPENSES                   = enum.auto() # Imposto de Renda e Contribuição Social sobre o Lucro
    CONTINUING_OPERATION_RESULTS   = enum.auto() # Resultado Líquido das Operações Continuadas
    DISCONTINUED_OPERATION_RESULTS = enum.auto() # Resultado Líquido das Operações Descontinuadas
    NET_PROFIT                     = enum.auto() # Lucro Líquido

_balance_info_by_group = {
    ReportGroup.DRE: {
        'Receita de Venda de Bens e/ou Serviços':                 (2, BalanceType.NET_INCOME),
        'Receitas de Intermediação Financeira':                   (2, BalanceType.NET_INCOME),
        'Receitas da Intermediação Financeira':                   (2, BalanceType.NET_INCOME),
        'Receitas das Operações':                                 (2, BalanceType.NET_INCOME),
        'Custo dos Bens e/ou Serviços Vendidos':                  (2, BalanceType.COST_OF_GOODS_SOLD),
        'Despesas de Intermediação Financeira':                   (2, BalanceType.COST_OF_GOODS_SOLD),
        'Despesas da Intermediação Financeira':                   (2, BalanceType.COST_OF_GOODS_SOLD),
        'Sinistros e Despesas das Operações':                     (2, BalanceType.COST_OF_GOODS_SOLD),
        'Resultado Bruto':                                        (2, BalanceType.GROSS_PROFIT),
        'Resultado Bruto de Intermediação Financeira':            (2, BalanceType.GROSS_PROFIT),
        'Resultado Bruto Intermediação Financeira':               (2, BalanceType.GROSS_PROFIT),
        'Despesas/Receitas Operacionais':                         (2, BalanceType.OPERATING_REVENUE_AND_EXPENSES),
        'Outras Despesas e Receitas Operacionais':                (2, BalanceType.OPERATING_REVENUE_AND_EXPENSES),
        'Outras Receitas e Despesas Operacionais':                (2, BalanceType.OPERATING_REVENUE_AND_EXPENSES),
        'Outras Despesas/Receitas Operacionais':                  (2, BalanceType.OPERATING_REVENUE_AND_EXPENSES),
        'Despesas Administrativas':                               (2, BalanceType.OPERATING_REVENUE_AND_EXPENSES),
        'Resultado de Equivalência Patrimonial':                  (2, BalanceType.OPERATING_REVENUE_AND_EXPENSES),
        'Resultado Antes do Resultado Financeiro e dos Tributos': (2, BalanceType.OPERATING_PROFIT),
        'Resultado Financeiro':                                   (2, BalanceType.FINANCIAL_RESULT),
        'Resultado Antes dos Tributos sobre o Lucro':             (2, BalanceType.EARNINGS_BEFORE_TAX),
        'Resultado antes dos Tributos sobre o Lucro':             (2, BalanceType.EARNINGS_BEFORE_TAX),
        'Imposto de Renda e Contribuição Social sobre o Lucro':   (2, BalanceType.TAX_EXPENSES),
        'Resultado Líquido das Operações Continuadas':            (2, BalanceType.CONTINUING_OPERATION_RESULTS),
        'Lucro ou Prejuízo das Operações Continuadas':            (2, BalanceType.CONTINUING_OPERATION_RESULTS),
        'Resultado Líquido de Operações Descontinuadas':          (2, BalanceType.DISCONTINUED_OPERATION_RESULTS),
        'Participações nos Lucros e Contribuições Estatutárias':  (2, BalanceType.NET_PROFIT),
        'Lucro ou Prejuízo Líquido Consolidado do Período':       (2, BalanceType.NET_PROFIT),
        'Lucro/Prejuízo Consolidado do Período':                  (2, BalanceType.NET_PROFIT)
    }
}

_report_groups_by_name = {
    'DF Consolidado - Balanço Patrimonial Ativo':                        (ReportGroup.BPA, True),
    'DF Individual - Balanço Patrimonial Ativo':                         (ReportGroup.BPA, False),
    'DF Consolidado - Balanço Patrimonial Passivo':                      (ReportGroup.BPP, True),
    'DF Individual - Balanço Patrimonial Passivo':                       (ReportGroup.BPP, False),
    'DF Consolidado - Demonstração do Resultado':                        (ReportGroup.DRE, True),
    'DF Individual - Demonstração do Resultado':                         (ReportGroup.DRE, False),
    'DF Consolidado - Demonstração de Resultado Abrangente':             (ReportGroup.DRA, True),
    'DF Individual - Demonstração de Resultado Abrangente':              (ReportGroup.DRA, False),
    'DF Consolidado - Demonstração do Fluxo de Caixa (Método Direto)':   (ReportGroup.DFC_MD, True),
    'DF Individual - Demonstração do Fluxo de Caixa (Método Direto)':    (ReportGroup.DFC_MD, False),
    'DF Consolidado - Demonstração do Fluxo de Caixa (Método Indireto)': (ReportGroup.DFC_MI, True),
    'DF Individual - Demonstração do Fluxo de Caixa (Método Indireto)':  (ReportGroup.DFC_MI, False),
    'DF Consolidado - Demonstração das Mutações do Patrimônio Líquido':  (ReportGroup.DMPL, True),
    'DF Individual - Demonstração das Mutações do Patrimônio Líquido':   (ReportGroup.DMPL, False),
    'DF Consolidado - Demonstração de Valor Adicionado':                 (ReportGroup.DVA, True),
    'DF Individual - Demonstração de Valor Adicionado':                  (ReportGroup.DVA, False)
}

def _read_report_date(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

def _read_report_group(group: str) -> Tuple[ReportGroup, bool]:
    try:
        return _report_groups_by_name[group]
    except KeyError:
        raise ValueError(f"unknown DFP group '{ group }'") from None

class _RawReport:
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

def _read_raw_reports(csv_file, delimiter: str) -> Iterable[_RawReport]:
    """Reads and returns DFP reports as an iterable of `_RawReport`s."""

    csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

    reports = {}
    prev_row = ''

    for row_index, row in enumerate(csv_reader):
        # Clean up duplicate rows. I don't know why, but some rows are duplicated.
        if row == prev_row:
            continue

        prev_row = row

        try:
            cvm_code        = row['CD_CVM']
            fiscal_year_end = row['DT_FIM_EXERC']
        except KeyError as e:
            logging.warn('failed to read row %d: %s', row_index, e)
            continue

        report_key = cvm_code + fiscal_year_end

        try:
            report = reports[report_key]
        except KeyError:
            report = _RawReport()

            try:
                report.reference_date    = row['DT_REFER']
                report.version           = row['VERSAO']
                report.group             = row['GRUPO_DFP']
                report.cnpj              = row['CNPJ_CIA']
                report.corporate_name    = row['DENOM_CIA']
                report.currency_name     = row['MOEDA']
                report.currency_size     = row['ESCALA_MOEDA']
                report.fiscal_year_start = row['DT_INI_EXERC'] if 'DT_INI_EXERC' in row else ''
                report.fiscal_year_order = row['ORDEM_EXERC']
            except KeyError as e:
                logging.warn('failed to read row %d: %s', row_index, e)
                continue

            report.cvm_code        = cvm_code
            report.fiscal_year_end = fiscal_year_end
            report.accounts        = []

            reports[report_key] = report
                
        report.accounts.append((row['CD_CONTA'], row['DS_CONTA'], row['VL_CONTA'], row['ST_CONTA_FIXA']))

    return reports.values()

def reader(csv_file, delimiter: str = ';') -> Generator[Report, None, None]:
    """Returns a generator that reads a DFP report from a CSV file."""

    for raw_report in _read_raw_reports(csv_file, delimiter):
        try:
            r = Report()
            r.version                = int(raw_report.version)
            r.group, r.consolidated  = _read_report_group(raw_report.group)
            r.company                = Company()
            r.company.cnpj           = raw_report.cnpj
            r.company.corporate_name = raw_report.corporate_name
            r.company.cvm_code       = raw_report.cvm_code
            r.currency               = normalize_currency(raw_report.currency_name)
            r.reference_date         = _read_report_date(raw_report.reference_date)
            r.fiscal_year_start      = _read_report_date(raw_report.fiscal_year_start) if raw_report.fiscal_year_start != '' else None
            r.fiscal_year_end        = _read_report_date(raw_report.fiscal_year_end)
            r.fiscal_year_order      = FiscalYearOrder(raw_report.fiscal_year_order)
            r.accounts               = []

            for code, name, quantity, is_fixed in raw_report.accounts:
                acc = Account()
                acc.code     = code
                acc.name     = name
                acc.quantity = normalize_quantity(float(quantity), raw_report.currency_size)
                acc.is_fixed = is_fixed == 'S'

                r.accounts.append(acc)
        except ValueError as exc:
            logging.warn(
                'failed to parse report of company %s (CVM: %s, fiscal year end: %s): %s',
                raw_report.corporate_name,
                raw_report.cvm_code,
                raw_report.fiscal_year_end,
                exc
            )

        yield r

def balances(report: Report) -> Dict[BalanceType, float]:
    balances = collections.defaultdict(float)
    
    for account in report.accounts:
        account_group = account.group()
        
        try:
            balance_info = _balance_info_by_group[account_group]

            required_level, balance_type = balance_info[account.name]
            
            if account.level == required_level:
                balances[balance_type] += account.quantity
        except KeyError:
            pass

    return balances