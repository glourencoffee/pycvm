import datetime
import unittest
from cvm.balances  import BalanceSheet
from cvm.datatypes import Currency, CurrencySize, Account, AccountTuple, BalanceType

class TestBalanceSheet(unittest.TestCase):
    def test_industrial_consolidated_2010(self):
        # BPA/2010 of "CENTRAIS ELET BRAS S.A. - ELETROBRAS" (ELET)
        bpa_accounts = AccountTuple(
            Currency.BRL,
            CurrencySize.THOUSAND,
            (
                Account('1',       'Ativo Total',                    146901002, True),
                Account('1.01',    'Ativo Circulante',               32805947,  True),
                Account('1.01.01', 'Caixa e Equivalentes de Caixa',  11278387,  True),
                Account('1.01.02', 'Aplicações Financeiras',         6774073,   True),
                Account('1.01.03', 'Contas a Receber',               4016006,   True),
                Account('1.01.04', 'Estoques',                       676609,    True),
                Account('1.01.05', 'Ativos Biológicos',              0,         True),
                Account('1.01.06', 'Tributos a Recuperar',           0,         True),
                Account('1.01.07', 'Despesas Antecipadas',           40418,     True),
                Account('1.01.08', 'Outros Ativos Circulantes',      10020454,  True),
                Account('1.02',    'Ativo Não Circulante',           114095055, True),
                Account('1.02.01', 'Ativo Realizável a Longo Prazo', 60423937,  True),
                Account('1.02.02', 'Investimentos',                  4724648,   True),
                Account('1.02.03', 'Imobilizado',                    46682498,  True),
                Account('1.02.04', 'Intangível',                     2263972,   True)
            )
        )

        # BPP/2010 of "CENTRAIS ELET BRAS S.A. - ELETROBRAS" (ELET)
        bpp_accounts = AccountTuple(
            Currency.BRL,
            CurrencySize.THOUSAND,
            (
                Account('2',       'Passivo Total',                      146901002, True),
                Account('2.01',    'Passivo Circulante',                 18369510,  True),
                Account('2.01.01', 'Obrigações Sociais e Trabalhistas',  772071,    True),
                Account('2.01.02', 'Fornecedores',                       5165765,   True),
                Account('2.01.03', 'Obrigações Fiscais',                 1102672,   True),
                Account('2.01.04', 'Empréstimos e Financiamentos',       1988948,   True),
                Account('2.01.05', 'Outras Obrigações',                  9082474,   True),
                Account('2.01.06', 'Provisões',                          257580,    True),
                Account('2.01.07', 'Passivos sobre Ativos Não-Correntes'
                                   ' a Venda e Descontinuados',          0,         True),
                Account('2.02',    'Passivo Não Circulante',             58001081,  True),
                Account('2.02.01', 'Empréstimos e Financiamentos',       32964518,  True),
                Account('2.02.02', 'Outras Obrigações',                  19541657,  True),
                Account('2.02.03', 'Tributos Diferidos',                 1217649,   True),
                Account('2.02.04', 'Provisões',                          3901289,   True),
                Account('2.02.05', 'Passivos sobre Ativos Não-Correntes'
                                   ' a Venda e Descontinuados',          375968,    True),
                Account('2.02.06', 'Lucros e Receitas a Apropriar',      0,         True),
                Account('2.03',    'Patrimônio Líquido Consolidado',     70530411,  True),
            )
        )

        b = BalanceSheet.from_accounts(
            bpa_accounts,
            bpp_accounts,
            BalanceType.CONSOLIDATED,
            datetime.date(2010, 12, 31)
        )

        self.assertEquals(b.total_assets,              146901002000)
        self.assertEquals(b.current_assets,            32805947000)
        self.assertEquals(b.cash_and_cash_equivalents, 11278387000)
        self.assertEquals(b.financial_investments,     6774073000)
        self.assertEquals(b.receivables,               4016006000)
        self.assertEquals(b.noncurrent_assets,         114095055000)
        self.assertEquals(b.investments,               4724648000)
        self.assertEquals(b.fixed_assets,              46682498000)
        self.assertEquals(b.intangible_assets,         2263972000)

        self.assertEquals(b.total_liabilities,              76370591000)
        self.assertEquals(b.current_liabilities,            18369510000)
        self.assertEquals(b.current_loans_and_financing,    1988948000)
        self.assertEquals(b.noncurrent_liabilities,         58001081000)
        self.assertEquals(b.noncurrent_loans_and_financing, 32964518000)

        self.assertEquals(b.equity, 70530411000)