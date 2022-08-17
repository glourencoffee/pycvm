import dataclasses
import decimal
from cvm.balances.balance import Balance

@dataclasses.dataclass(init=True, frozen=True)
class IndustrialBPA(Balance):
    total_assets: decimal.Decimal
    """Ativo Total"""

    current_assets: decimal.Decimal
    """Ativo Circulante"""
    
    cash_and_cash_equivalents: decimal.Decimal
    """Caixa e Equivalentes de Caixa"""
    
    financial_investments: decimal.Decimal
    """Aplicações Financeiras"""
    
    accounts_receivable: decimal.Decimal
    """Contas a Receber"""
    
    inventories: decimal.Decimal
    """Estoques"""

    biological_assets: decimal.Decimal
    """Ativos Biológicos"""

    taxes_recoverable: decimal.Decimal
    """Tributos a Recuperar"""

    prepaid_expenses: decimal.Decimal
    """Despesas Antecipadas"""

    other_current_assets: decimal.Decimal
    """Outros Ativos Circulantes"""
    
    noncurrent_assets: decimal.Decimal
    """Ativo Não Circulante"""
    
    long_term_assets: decimal.Decimal
    """Ativo Realizável a Longo Prazo"""
    
    long_term_investments: decimal.Decimal
    """Investimentos a Longo Prazo"""
    
    fixed_assets: decimal.Decimal
    """Ativo Imobilizado"""
    
    intangible_assets: decimal.Decimal
    """Ativo Intangível"""

    __individual_layout__ = \
    __consolidated_layout__ = (
        ('1',       'Ativo Total',                    'total_assets'),
        ('1.01',    'Ativo Circulante',               'current_assets'),
        ('1.01.01', 'Caixa e Equivalentes de Caixa',  'cash_and_cash_equivalents'),
        ('1.01.02', 'Aplicações Financeiras',         'financial_investments'),
        ('1.01.03', 'Contas a Receber',               'accounts_receivable'),
        ('1.01.04', 'Estoques',                       'inventories'),
        ('1.01.05', 'Ativos Biológicos',              'biological_assets'),
        ('1.01.06', 'Tributos a Recuperar',           'taxes_recoverable'),
        ('1.01.07', 'Despesas Antecipadas',           'prepaid_expenses'),
        ('1.01.08', 'Outros Ativos Circulantes',      'other_current_assets'),
        ('1.02',    'Ativo Não Circulante',           'noncurrent_assets'),
        ('1.02.01', 'Ativo Realizável a Longo Prazo', 'long_term_assets'),
        ('1.02.02', 'Investimentos',                  'long_term_investments'),
        ('1.02.03', 'Imobilizado',                    'fixed_assets'),
        ('1.02.04', 'Intangível',                     'intangible_assets')
    )

    __slots__ = (
        'total_assets',
        'current_assets',
        'cash_and_cash_equivalents',
        'financial_investments',
        'accounts_receivable',
        'inventories',
        'biological_assets',
        'taxes_recoverable',
        'prepaid_expenses',
        'other_current_assets',
        'noncurrent_assets',
        'long_term_assets',
        'long_term_investments',
        'fixed_assets',
        'intangible_assets'
    )

    def validate(self):
        current_assets = (
            self.cash_and_cash_equivalents +
            self.financial_investments +
            self.accounts_receivable +
            self.inventories +
            self.biological_assets +
            self.taxes_recoverable +
            self.prepaid_expenses +
            self.other_current_assets
        )

        if current_assets != self.current_assets:
            raise ValueError(f"sum of discriminated current assets ({ current_assets }) != 'current_assets' ({ self.current_assets })")

        noncurrent_assets = (
            self.long_term_assets +
            self.long_term_investments +
            self.fixed_assets +
            self.intangible_assets
        )

        if noncurrent_assets != self.noncurrent_assets:
            raise ValueError(f"sum of discriminated noncurrent assets ({ noncurrent_assets }) != 'noncurrent_assets' ({ self.noncurrent_assets })")

        total_assets = current_assets + noncurrent_assets

        if total_assets != self.total_assets:
            raise ValueError(f"'current_assets' + 'noncurrent_assets' ({ total_assets }) != 'total_assets' ({ self.total_assets })")