import functools
import typing
from cvm import balances

def make_layout_2010_last() -> balances.AccountLayout:
    l = balances.AccountLayout(2010)
    l.add('1',       'Ativo Total',                    'total_assets')
    l.add('1.01',    'Ativo Circulante',               'current_assets')
    l.add('1.01.01', 'Caixa e Equivalentes de Caixa',  'cash_and_cash_equivalents')
    l.add('1.01.02', 'Aplicações Financeiras',         'financial_investments')
    l.add('1.01.03', 'Contas a Receber',               'receivables')
    l.add('1.01.04', 'Estoques')
    l.add('1.01.05', 'Ativos Biológicos')
    l.add('1.01.06', 'Tributos a Recuperar')
    l.add('1.01.07', 'Despesas Antecipadas')
    l.add('1.01.08', 'Outros Ativos Circulantes')
    l.add('1.02',    'Ativo Não Circulante',           'noncurrent_assets')
    l.add('1.02.01', 'Ativo Realizável a Longo Prazo')
    l.add('1.02.02', 'Investimentos',                  'investments')
    l.add('1.02.03', 'Imobilizado',                    'fixed_assets')
    l.add('1.02.04', 'Intangível',                     'intangible_assets')

    return l

@functools.lru_cache
def _get_layouts():
    return (
        make_layout_2010_last(),
    )

class IndustrialBPAValidator(balances.AccountLayoutValidator):
    def individual_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_layouts()

    def consolidated_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_layouts()