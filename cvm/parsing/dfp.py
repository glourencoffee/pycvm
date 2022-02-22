import enum
import collections
import datetime
import csv
from typing                import Optional, Generator, Tuple, Dict
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
    # TODO

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

def reader(csv_file, delimiter: str = ';') -> Generator[Report, None, None]:
    """Returns a generator that reads a DFP report from a CSV file."""

    csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

    reports = {}

    for row_number, row in enumerate(csv_reader):
        try:
            cvm_code          = row['CD_CVM']
            fiscal_year_end   = _read_report_date(row['DT_FIM_EXERC'])

            try:
                # Look up for a cached report on this fiscal year.
                report = reports[fiscal_year_end.year]

                # A report was found. Now check if this row's CVM code matches the cached report's.
                if cvm_code != report.company.cvm_code:
                    # Mismatching CVM code. That means we're getting rows of a new company,
                    # so generate (yield) all cached reports.
                    for r in reports.values():
                        yield r

                    # Reset cache and fallthrough, so as to cache up this row's remaining data.
                    reports = {}
                    report = None
                else:
                    # This row's CVM code is same as the one before. That means we're still reading
                    # data of the same company, so fallthrough and read this row's account data.
                    pass

            except KeyError:
                # No report found. This happens while reading the first rows.
                report = None

            if report is None:


                report = Report()
                report.version                    = int(row['VERSAO'])
                report.group, report.consolidated = _read_report_group(row['GRUPO_DFP'])
                report.company                    = Company()
                report.company.cnpj               = row['CNPJ_CIA']
                report.company.cvm_code           = cvm_code
                report.company.corporate_name        = row['DENOM_CIA']
                report.currency                   = normalize_currency(row['MOEDA'])
                report.accounts                   = []
                report.reference_date             = _read_report_date(row['DT_REFER'])
                report.fiscal_year_start          = _read_report_date(row['DT_INI_EXERC']) if 'DT_INI_EXERC' in row else None
                report.fiscal_year_end            = fiscal_year_end
                report.fiscal_year_order          = FiscalYearOrder(row['ORDEM_EXERC'])

                reports[fiscal_year_end.year] = report

            account = Account()
            account.code     = row['CD_CONTA']
            account.name     = row['DS_CONTA']
            account.quantity = normalize_quantity(float(row['VL_CONTA']), row['ESCALA_MOEDA'])
            account.is_fixed = row['ST_CONTA_FIXA'] == 'S'
            report.accounts.append(account)
        except ValueError as e:
            raise ValueError(f'at row { row_number }: { e }') from None
    
    for r in reports.values():
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