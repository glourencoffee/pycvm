import functools
import typing
from cvm.balances.common.dre import CommonDREValidator
from cvm.balances.account_layout import AccountLayout

def make_individual_layout_2010_last() -> AccountLayout:
    l = AccountLayout(2010)
    l.add('3.01', 'Receitas das Operações',                                 'revenue')
    l.add('3.02', 'Sinistros e Despesas das Operações',                     'costs')
    l.add('3.03', 'Resultado Bruto',                                        'gross_profit')
    l.add('3.04', 'Despesas Administrativas',                               '_administrative_expenses')
    l.add('3.05', 'Outras Receitas e Despesas Operacionais',                'operating_income_and_expenses')
    l.add('3.06', 'Resultado de Equivalência Patrimonial',                  '_equity_method_income')
    l.add('3.07', 'Resultado Antes do Resultado Financeiro e dos Tributos', 'operating_profit')
    l.add('3.08', 'Resultado Financeiro',                                   'nonoperating_result')
    l.add('3.09', 'Resultado Antes dos Tributos sobre o Lucro',             'earnings_before_tax')
    l.add('3.10', 'Imposto de Renda e Contribuição Social sobre o Lucro',   'tax_expenses')
    l.add('3.11', 'Resultado Líquido das Operações Continuadas',            'continuing_operation_result')
    l.add('3.12', 'Resultado Líquido de Operações Descontinuadas',          'discontinued_operation_result')
    l.add('3.13', 'Lucro/Prejuízo do Período',                              'net_income')

    return l

def make_consolidated_layout_2010_last() -> AccountLayout:
    l = make_individual_layout_2010_last()
    l.add('3.13', 'Lucro/Prejuízo Consolidado do Período', 'net_income')

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

class InsuranceDREValidator(CommonDREValidator):
    def individual_layouts(self) -> typing.Iterable[AccountLayout]:
        return _get_individual_layouts()

    def consolidated_layouts(self) -> typing.Iterable[AccountLayout]:
        return _get_consolidated_layouts()

    def _finish(self, attributes: typing.Dict[str, int]):
        adm_expenses = attributes.pop('_administrative_expenses')
        eqm_income   = attributes.pop('_equity_method_income')

        attributes['nonoperating_result'] += adm_expenses + eqm_income

        super()._finish(attributes)