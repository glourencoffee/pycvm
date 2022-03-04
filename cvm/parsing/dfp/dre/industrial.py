from typing                  import Optional, Iterable
from cvm.parsing.dfp.account import Account
from cvm.parsing.dfp.balance import Balance

class IndustrialCompanyBalance(Balance):
    __layout__ = (
        ('3.01', 'Receita de Venda de Bens e/ou Serviços',                 '_net_income'),
        ('3.02', 'Custo dos Bens e/ou Serviços Vendidos',                  '_cost_of_goods_sold'),
        ('3.03', 'Resultado Bruto',                                        '_gross_profit'),
        ('3.04', 'Despesas/Receitas Operacionais',                         '_operating_revenue_and_expenses'),
        ('3.05', 'Resultado Antes do Resultado Financeiro e dos Tributos', '_operating_profit'),
        ('3.06', 'Resultado Financeiro',                                   '_financial_result'),
        ('3.07', 'Resultado Antes dos Tributos sobre o Lucro',             '_earnings_before_tax'),
        ('3.08', 'Imposto de Renda e Contribuição Social sobre o Lucro',   '_tax_expenses'),
        ('3.09', 'Resultado Líquido das Operações Continuadas',            '_continuing_operation_result'),
        ('3.10', 'Resultado Líquido de Operações Descontinuadas',          '_discontinued_operation_result'),
        ('3.11', 'Lucro/Prejuízo Consolidado do Período',                  '_net_profit'),
    )

    __slots__ = [
        '_net_income',
        '_cost_of_goods_sold',
        '_gross_profit',
        '_operating_revenue_and_expenses',
        '_operating_result',
        '_depreciation_and_amortization',
        '_operating_profit',
        '_financial_result',
        '_earnings_before_tax',
        '_tax_expenses',
        '_continuing_operation_result',
        '_discontinued_operation_result',
        '_net_profit',
        '_da_found_count'
    ]

    def __init__(self, accounts: Iterable[Account]):
        self._da_found_count = 0
        self._depreciation_and_amortization = None
        
        super().__init__(accounts)

        if self._depreciation_and_amortization is None:
            self._operating_result = None
        else:
            # EBITDA = EBIT + DA
            self._operating_result = self.operating_profit + abs(self._depreciation_and_amortization)

    def parse_other(self, account: Account):
        if self._da_found_count == 2:
            return

        # Check if this is an amortization or depreciation account.
        #
        # Amortization and depreciation accounts are non-fixed. That means they are not
        # predefined as part of an account layout but rather by whoever sent the company's
        # data using the ENET software. However, since the chosen name must make sense to
        # the person who's reading the data (the investor or else), we can check for
        # sensible names. Here are some examples of chosen names:
        # - Depreciação e Amortização
        # - Depreciação e Amortizacão
        # - Depreciações e Amortização
        # - Depreciação/Amortização
        #
        # So, by checking for 'deprecia' and 'amortiza', we cover pretty much all cases.
        #
        # Also, there are reports that separate depreciation and amortization into two accounts,
        # which is also covered up by keeping a counter.
        lcname       = account.name.lower()
        has_deprecia = 'deprecia' in lcname
        has_amortiza = 'amortiza' in lcname

        if has_deprecia and has_amortiza:
            self._depreciation_and_amortization = account.quantity
            self._da_found_count = 2
        elif has_deprecia or has_amortiza:
            self._da_found_count += 1

            if self._da_found_count == 1:
                self._depreciation_and_amortization = account.quantity
            else:
                self._depreciation_and_amortization += account.quantity

    def validate(self):
        # TODO
        pass

    @property
    def net_income(self) -> float:
        """Receita Líquida"""

        return self._net_income
    
    @property
    def cost_of_goods_sold(self) -> float:
        """Custos das Mercadorias Vendidas (COGS)"""

        return self._cost_of_goods_sold
    
    @property
    def gross_profit(self) -> float:
        """Lucro Bruto"""

        return self._gross_profit
    
    @property
    def operating_revenue_and_expenses(self) -> float:
        """Receitas e Despesas Operacionais"""

        return self._operating_revenue_and_expenses
    
    @property
    def operating_result(self) -> Optional[float]:
        """Resultado Operacional (EBITDA)"""

        return self._operating_result
    
    @property
    def depreciation_and_amortization(self) -> Optional[float]:
        """Depreciação e Amortização"""

        return self._depreciation_and_amortization
    
    @property
    def operating_profit(self) -> float:
        """Lucro Operacional (EBIT)"""

        return self._operating_profit
    
    @property
    def financial_result(self) -> float:
        """Resultado Financeiro"""

        return self._financial_result
    
    @property
    def earnings_before_tax(self) -> float:
        """Resultado Antes dos Tributos sobre o Lucro (EBT)"""

        return self._earnings_before_tax
    
    @property
    def tax_expenses(self) -> float:
        """Imposto de Renda e Contribuição Social sobre o Lucro"""

        return self._tax_expenses
    
    @property
    def continuing_operation_result(self) -> float:
        """Resultado Líquido das Operações Continuadas"""

        return self._continuing_operation_result
    
    @property
    def discontinued_operation_result(self) -> float:
        """Resultado Líquido das Operações Descontinuadas"""

        return self._discontinued_operation_result
    
    @property
    def net_profit(self) -> float:
        """Lucro Líquido"""

        return self._net_profit