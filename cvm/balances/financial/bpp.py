import functools
import typing
from cvm import balances

def make_individual_layout_2010_2019() -> balances.AccountLayout:
    l = balances.AccountLayout(2010, 2019)
    l.add('2',    'Passivo Total',                                                'total_liabilities')
    l.add('2.01', 'Passivos Financeiros para Negociação')
    l.add('2.02', 'Outros Passivos Financeiros ao Valor Justo no Resultado')
    l.add('2.03', 'Passivos Financeiros ao Custo Amortizado')
    l.add('2.04', 'Provisões')
    l.add('2.05', 'Passivos Fiscais')
    l.add('2.06', 'Outros Passivos')
    l.add('2.07', 'Passivos sobre Ativos Não Correntes a Venda e Descontinuados')
    l.add('2.08', 'Patrimônio Líquido',                                           'equity')

    return l

def make_consolidated_layout_2010_2019() -> balances.AccountLayout:
    l = make_individual_layout_2010_2019()
    l.add('2.08', 'Patrimônio Líquido Consolidado', 'equity')

    return l

def make_individual_layout_2020_last() -> balances.AccountLayout:
    l = balances.AccountLayout(2020)
    l.add('2',    'Passivo Total',                                                      'total_liabilities')
    l.add('2.01', 'Passivos Financeiros Avaliados ao Valor Justo através do Resultado')
    l.add('2.02', 'Passivos Financeiros ao Custo Amortizado')
    l.add('2.03', 'Provisões')
    l.add('2.04', 'Passivos Fiscais')
    l.add('2.05', 'Outros Passivos')
    l.add('2.06', 'Passivos sobre Ativos Não Correntes a Venda e Descontinuados')
    l.add('2.07', 'Patrimônio Líquido',                                                 'equity')

    return l

def make_consolidated_layout_2020_last() -> balances.AccountLayout:
    l = make_individual_layout_2020_last()
    l.add('2.07', 'Patrimônio Líquido Consolidado', 'equity')

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

class FinancialBPPValidator(balances.AccountLayoutValidator):
    def individual_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_individual_layouts()

    def consolidated_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_consolidated_layouts()

    def _finish(self, attributes: typing.Dict[str, int]):
        attributes['current_liabilities']            = None
        attributes['current_loans_and_financing']    = None
        attributes['noncurrent_liabilities']         = None
        attributes['noncurrent_loans_and_financing'] = None
        attributes['total_liabilities']              -= attributes['equity']