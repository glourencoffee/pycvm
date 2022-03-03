import unittest
from cvm.parsing.dfp.account import Account
from cvm.parsing.dfp.bpa     import IndustrialCompanyBalance

class TestBPA(unittest.TestCase):
    def test_industrial(self):
        # BPA/2010 of CENTRAIS ELET BRAS S.A. - ELETROBRAS (ELET)
        accounts = [
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
        ]

        balance = IndustrialCompanyBalance(iter(accounts))
        balance.validate()

        self.assertEquals(balance.total_assets,              146901002)
        self.assertEquals(balance.current_assets,            32805947)
        self.assertEquals(balance.cash_and_cash_equivalents, 11278387)
        self.assertEquals(balance.financial_investments,     6774073)
        self.assertEquals(balance.accounts_receivable,       4016006)
        self.assertEquals(balance.inventories,               676609)
        self.assertEquals(balance.biological_assets,         0)
        self.assertEquals(balance.taxes_recoverable,         0)
        self.assertEquals(balance.prepaid_expenses,          40418)
        self.assertEquals(balance.other_current_assets,      10020454)
        self.assertEquals(balance.noncurrent_assets,         114095055)
        self.assertEquals(balance.long_term_assets,          60423937)
        self.assertEquals(balance.long_term_investiments,    4724648)
        self.assertEquals(balance.fixed_assets,              46682498)
        self.assertEquals(balance.intangible_assets,         2263972)