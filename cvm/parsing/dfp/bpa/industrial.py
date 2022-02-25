from cvm.parsing.dfp.balance import Balance

class IndustrialCompanyBalance(Balance):
    _layout = [
        ('1',       'Ativo Total',                    '_total_assets'),
        ('1.01',    'Ativo Circulante',               '_current_assets'),
        ('1.01.01', 'Caixa e Equivalentes de Caixa',  '_cash_and_cash_equivalents'),
        ('1.01.02', 'Aplicações Financeiras',         '_financial_investments'),
        ('1.01.03', 'Contas a Receber',               '_accounts_receivable'),
        ('1.01.04', 'Estoques',                       '_inventories'),
        ('1.01.05', 'Ativos Biológicos',              '_biological_assets'),
        ('1.01.06', 'Tributos a Recuperar',           '_taxes_recoverable'),
        ('1.01.07', 'Despesas Antecipadas',           '_prepaid_expenses'),
        ('1.01.08', 'Outros Ativos Circulantes',      '_other_current_assets'),
        ('1.02',    'Ativo Não Circulante',           '_noncurrent_assets'),
        ('1.02.01', 'Ativo Realizável a Longo Prazo', '_long_term_assets'),
        ('1.02.02', 'Investimentos',                  '_long_term_investiments'),
        ('1.02.03', 'Imobilizado',                    '_fixed_assets'),
        ('1.02.04', 'Intangível',                     '_intangible_assets')
    ]

    __slots__ = [
        '_total_assets',
        '_current_assets',
        '_cash_and_cash_equivalents',
        '_financial_investments',
        '_accounts_receivable',
        '_inventories',
        '_biological_assets',
        '_taxes_recoverable',
        '_prepaid_expenses',
        '_other_current_assets',
        '_noncurrent_assets',
        '_long_term_assets',
        '_long_term_investiments',
        '_fixed_assets',
        '_intangible_assets'
    ]

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
            self.long_term_investiments +
            self.fixed_assets +
            self.intangible_assets
        )

        if noncurrent_assets != self.noncurrent_assets:
            raise ValueError(f"sum of discriminated noncurrent assets ({ noncurrent_assets }) != 'noncurrent_assets' ({ self.noncurrent_assets })")

        total_assets = current_assets + noncurrent_assets

        if total_assets != self.total_assets:
            raise ValueError(f"'current_assets' + 'noncurrent_assets' ({ total_assets }) != 'total_assets' ({ self.total_assets })")

    @property
    def total_assets(self) -> float:
        """Ativo Total"""

        return self._total_assets

    @property
    def current_assets(self) -> float:
        """Ativo Circulante"""

        return self._current_assets
    
    @property
    def cash_and_cash_equivalents(self) -> float:
        """Caixa e Equivalentes de Caixa"""

        return self._cash_and_cash_equivalents
    
    @property
    def financial_investments(self) -> float:
        """Aplicações Financeiras"""

        return self._financial_investments
    
    @property
    def accounts_receivable(self) -> float:
        """Contas a Receber"""

        return self._accounts_receivable
    
    @property
    def inventories(self) -> float:
        """Estoques"""

        return self._inventories

    @property
    def biological_assets(self) -> float:
        """Ativos Biológicos"""

        return self._biological_assets

    @property
    def taxes_recoverable(self) -> float:
        """Tributos a Recuperar"""

        return self._taxes_recoverable

    @property
    def prepaid_expenses(self) -> float:
        """Despesas Antecipadas"""

        return self._prepaid_expenses

    @property
    def other_current_assets(self) -> float:
        """Outros Ativos Circulantes"""

        return self._other_current_assets
    
    @property
    def noncurrent_assets(self) -> float:
        """Ativo Não Circulante"""

        return self._noncurrent_assets
    
    @property
    def long_term_assets(self) -> float:
        """Ativo Realizável a Longo Prazo"""

        return self._long_term_assets
    
    @property
    def long_term_investiments(self) -> float:
        """Investimentos a Longo Prazo"""

        return self._long_term_investiments
    
    @property
    def fixed_assets(self) -> float:
        """Ativo Imobilizado"""

        return self._fixed_assets
    
    @property
    def intangible_assets(self) -> float:
        """Ativo Intangível"""

        return self._intangible_assets