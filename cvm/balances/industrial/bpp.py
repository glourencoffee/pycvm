import functools
import typing
from cvm import balances

def make_individual_layout_2010_last() -> balances.AccountLayout:
    l = balances.AccountLayout(2010)
    l.add('2',        'Passivo Total',                      'total_liabilities')
    l.add('2.01',     'Passivo Circulante',                 'current_liabilities')
    l.add('2.01.01',  'Obrigações Sociais e Trabalhistas')
    l.add('2.01.02',  'Fornecedores')
    l.add('2.01.03',  'Obrigações Fiscais')
    l.add('2.01.04',  'Empréstimos e Financiamentos',       'current_loans_and_financing')
    l.add('2.01.05',  'Outras Obrigações')
    l.add('2.01.06',  'Provisões')
    l.add('2.01.07',  'Passivos sobre Ativos Não-Correntes'
                      ' a Venda e Descontinuados')
    l.add('2.02',     'Passivo Não Circulante',             'noncurrent_liabilities')
    l.add('2.02.01',  'Empréstimos e Financiamentos',       'noncurrent_loans_and_financing')
    l.add('2.02.02',  'Outras Obrigações')
    l.add('2.02.03',  'Tributos Diferidos')
    l.add('2.02.04',  'Provisões')
    l.add('2.02.05',  'Passivos sobre Ativos Não-Correntes'
                      ' a Venda e Descontinuados')
    l.add('2.02.06',  'Lucros e Receitas a Apropriar')
    l.add('2.03',     'Patrimônio Líquido',                 'equity')

    return l

def make_consolidated_layout_2010_last() -> balances.AccountLayout:
    l = make_individual_layout_2010_last()
    l.add('2.03', 'Patrimônio Líquido Consolidado', 'equity')

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

class IndustrialBPPValidator(balances.AccountLayoutValidator):
    def individual_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_individual_layouts()
    
    def consolidated_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_consolidated_layouts()

    def _finish(self, attributes: typing.Dict[str, int]):
        attributes['total_liabilities'] -= attributes['equity']