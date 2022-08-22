import functools
import typing
from cvm.balances.common.dre import CommonDREValidator
from cvm.balances.account_layout import AccountLayout

def make_individual_layout_2010_last() -> AccountLayout:
    l = AccountLayout(2010)
    l.add('3.01', 'Receita de Venda de Bens e/ou Serviços',                 'revenue')
    l.add('3.02', 'Custo dos Bens e/ou Serviços Vendidos',                  'costs')
    l.add('3.03', 'Resultado Bruto',                                        'gross_profit')
    l.add('3.04', 'Despesas/Receitas Operacionais',                         'operating_income_and_expenses')
    l.add('3.05', 'Resultado Antes do Resultado Financeiro e dos Tributos', 'operating_profit')
    l.add('3.06', 'Resultado Financeiro',                                   'nonoperating_result')
    l.add('3.07', 'Resultado Antes dos Tributos sobre o Lucro',             'earnings_before_tax')
    l.add('3.08', 'Imposto de Renda e Contribuição Social sobre o Lucro',   'tax_expenses')
    l.add('3.09', 'Resultado Líquido das Operações Continuadas',            'continuing_operation_result')
    l.add('3.10', 'Resultado Líquido de Operações Descontinuadas',          'discontinued_operation_result')
    l.add('3.11', 'Lucro/Prejuízo do Período',                              'net_income')

    return l

def make_consolidated_layout_2010_last() -> AccountLayout:
    l = make_individual_layout_2010_last()
    l.add('3.11', 'Lucro/Prejuízo Consolidado do Período', 'net_income')

    return l

@functools.lru_cache
def _get_individual_layouts():
    return (
        make_individual_layout_2010_last(),
    )

@functools.lru_cache
def _get_consolidated_layouts():
    return (
        make_consolidated_layout_2010_last(),
    )

class IndustrialDREValidator(CommonDREValidator):
    def individual_layouts(self) -> typing.Iterable[AccountLayout]:
        return _get_individual_layouts()

    def consolidated_layouts(self) -> typing.Iterable[AccountLayout]:
        return _get_consolidated_layouts()