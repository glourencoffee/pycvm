import functools
import typing
from cvm import balances

def make_layout_2010_2017() -> balances.AccountLayout:
    l = balances.AccountLayout(2010, 2017)
    l.add('1',    'Ativo Total',                   'total_assets')
    l.add('1.01', 'Caixa e Equivalentes de Caixa', 'cash_and_cash_equivalents')
    l.add('1.02', 'Aplicações Financeiras',        'financial_investments')
    l.add('1.03', 'Empréstimos e Recebíveis',      'receivables')
    l.add('1.04', 'Tributos Diferidos'),
    l.add('1.05', 'Outros Ativos')
    l.add('1.06', 'Investimentos',                 'investments')
    l.add('1.07', 'Imobilizado',                   'fixed_assets')
    l.add('1.08', 'Intangível',                    'intangible_assets')

    return l

def make_layout_2018_2019() -> balances.AccountLayout:
    l = balances.AccountLayout(2018, 2019)
    l.add('1',    'Ativo Total',                   'total_assets')
    l.add('1.01', 'Caixa e Equivalentes de Caixa', 'cash_and_cash_equivalents')
    l.add('1.02', 'Ativos Financeiros',            'financial_investments')
    l.add('1.03', 'Tributos Diferidos')
    l.add('1.04', 'Outros Ativos')
    l.add('1.05', 'Investimentos',                 'investments')
    l.add('1.06', 'Imobilizado',                   'fixed_assets')
    l.add('1.07', 'Intangível',                    'intangible_assets')

    return l

def make_layout_2020_last() -> balances.AccountLayout:
    l = balances.AccountLayout(2020)
    l.add('1',    'Ativo Total',                   'total_assets')
    l.add('1.01', 'Caixa e Equivalentes de Caixa', 'cash_and_cash_equivalents')
    l.add('1.02', 'Ativos Financeiros',            'financial_investments')
    l.add('1.03', 'Tributos')
    l.add('1.04', 'Outros Ativos')
    l.add('1.05', 'Investimentos',                 'investments')
    l.add('1.06', 'Imobilizado',                   'fixed_assets')
    l.add('1.07', 'Intangível',                    'intangible_assets')

    return l

@functools.lru_cache
def _get_layouts():
    return (
        make_layout_2010_2017(),
        make_layout_2018_2019(),
        make_layout_2020_last()
    )

class FinancialBPAValidator(balances.AccountLayoutValidator):
    def individual_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_layouts()

    def consolidated_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_layouts()

    def _finish(self, attributes: typing.Dict[str, int]):
        if 'receivables' not in attributes:
            attributes['receivables'] = 0

        attributes['current_assets']    = None
        attributes['noncurrent_assets'] = None