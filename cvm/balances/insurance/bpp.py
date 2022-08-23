import functools
import typing
from cvm import balances

def make_layout_2010_last() -> balances.AccountLayout:
    l = balances.AccountLayout(2010)
    l.add('2',       'Passivo Total',                  'total_liabilities')
    l.add('2.01',    'Passivo Circulante',             'current_liabilities')
    l.add('2.02',    'Passivo Não Circulante',         'noncurrent_liabilities')
    l.add('2.03',    'Patrimônio Líquido Consolidado', 'equity')

    return l

@functools.lru_cache
def _get_layouts():
    return (
        make_layout_2010_last(),
    )

class InsuranceBPPValidator(balances.AccountLayoutValidator):
    def individual_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_layouts()

    def consolidated_layouts(self) -> typing.Iterable[balances.AccountLayout]:
        return _get_layouts()

    def _finish(self, attributes: typing.Dict[str, int]):
        attributes['total_liabilities']             -= attributes['equity']
        attributes['current_loans_and_financing']    = None
        attributes['noncurrent_loans_and_financing'] = None