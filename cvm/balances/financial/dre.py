import functools
import typing
from cvm.balances.common.dre     import CommonDREValidator
from cvm.balances.account_layout import AccountLayout

def make_individual_layout_2010_2019() -> AccountLayout:
    l = AccountLayout(2010, 2019)
    l.add('3.01', 'Receitas da Intermediação Financeira',                 'revenue')
    l.add('3.02', 'Despesas da Intermediação Financeira',                 'costs')
    l.add('3.03', 'Resultado Bruto Intermediação Financeira',             'gross_profit')
    l.add('3.04', 'Outras Despesas/Receitas Operacionais',                'operating_income_and_expenses')
    l.add('3.05', 'Resultado Antes dos Tributos sobre o Lucro',           'earnings_before_tax')
    l.add('3.06', 'Imposto de Renda e Contribuição Social sobre o Lucro', 'tax_expenses')
    l.add('3.07', 'Resultado Líquido das Operações Continuadas',          'continuing_operation_result')
    l.add('3.08', 'Resultado Líquido das Operações Descontinuadas',       'discontinued_operation_result')
    l.add('3.09', 'Lucro/Prejuízo do Período',                            'net_income')

    return l

def make_consolidated_layout_2010_2019() -> AccountLayout:
    l = make_individual_layout_2010_2019()
    l.add('3.09', 'Lucro/Prejuízo Consolidado do Período', 'net_income')

    return l

def make_individual_layout_2020_last() -> AccountLayout:
    l = AccountLayout(2020)
    l.add('3.01', 'Receitas de Intermediação Financeira',                   'revenue')
    l.add('3.02', 'Despesas de Intermediação Financeira',                   'costs')
    l.add('3.03', 'Resultado Bruto de Intermediação Financeira',            'gross_profit')
    l.add('3.04', 'Outras Despesas e Receitas Operacionais',                'operating_income_and_expenses')
    l.add('3.05', 'Resultado antes dos Tributos sobre o Lucro',             'earnings_before_tax')
    l.add('3.06', 'Imposto de Renda e Contribuição Social sobre o Lucro',   'tax_expenses')
    l.add('3.07', 'Lucro ou Prejuízo das Operações Continuadas',            'continuing_operation_result')
    l.add('3.08', 'Resultado Líquido das Operações Descontinuadas',         'discontinued_operation_result')
    l.add('3.09', 'Lucro ou Prejuízo antes das '
                  'Participações e Contribuições Estatutárias')
    l.add('3.10', 'Participações nos Lucros e Contribuições Estatutárias')
    l.add('3.11', 'Lucro ou Prejuízo Líquido do Período',                   'net_income')
    
    return l

def make_consolidated_layout_2020_last() -> AccountLayout:
    l = make_individual_layout_2020_last()
    l.add('3.11', 'Lucro ou Prejuízo Líquido Consolidado do Período', 'net_income')

    return l

@functools.lru_cache
def _get_individual_layouts():
    return (
        make_individual_layout_2010_2019(),
        make_individual_layout_2020_last()
    )

@functools.lru_cache
def _get_consolidated_layouts():
    return (
        make_consolidated_layout_2010_2019(),
        make_consolidated_layout_2020_last()
    )

class FinancialDREValidator(CommonDREValidator):
    def individual_layouts(self) -> typing.Iterable[AccountLayout]:
        return _get_individual_layouts()

    def consolidated_layouts(self) -> typing.Iterable[AccountLayout]:
        return _get_consolidated_layouts()
    
    def _finish(self, attributes: typing.Dict[str, int]):
        attributes['operating_profit']    = attributes['earnings_before_tax']
        attributes['nonoperating_result'] = 0

        super()._finish(attributes)