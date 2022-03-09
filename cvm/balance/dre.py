import dataclasses
import decimal
import typing
from cvm.balance.balance   import Balance, AccountParser
from cvm.datatypes.account import Account

class IndustrialDREParser(AccountParser):
    __slots__ = ('_da', '_da_found_count')

    def __init__(self):
        self._da = None
        self._da_found_count = 0

    def parse(self, account: Account):
        if self._da_found_count == 2:
            return

        ################################################################################
        # Check if this is an amortization or depreciation account.
        #
        # Amortization and depreciation accounts are non-fixed. That means they are not
        # predefined but rather chosen by whoever sent the company's data using the ENET
        # software. However, since the chosen name must make sense to the person who's
        # reading the data (the investor or else), we can check for sensible names. Here
        # are some examples of chosen names:
        # - Depreciação e Amortização
        # - Depreciação e Amortizacão
        # - Depreciações e Amortização
        # - Depreciação/Amortização
        #
        # Moreover, some companies discriminate their depreciation and amortization into
        # two accounts, while others keep it in only one:
        # - Depreciação
        # - Amortização
        # 
        # That's what the counter is for: in case there's more than one account, their
        # quantities are summed up into a single D&A variable.
        # 
        # Now, regarding the account's name, by checking for lowercase 'deprecia' and/or
        # 'amortiza', we cover pretty much all cases.
        ################################################################################
        lcname       = account.name.lower()
        has_deprecia = 'deprecia' in lcname
        has_amortiza = 'amortiza' in lcname

        if has_deprecia and has_amortiza:
            self._da = account.quantity
            self._da_found_count = 2
            
        elif has_deprecia or has_amortiza:
            self._da_found_count += 1

            if self._da_found_count == 1:
                self._da = account.quantity
            else:
                self._da += account.quantity

    def finish(self, attributes: typing.Dict[str, decimal.Decimal]):
        if self._da is None:
            operating_result = None
        else:
            # EBITDA = EBIT + DA
            operating_result = attributes['operating_profit'] + abs(self._da)
        
        attributes['depreciation_and_amortization'] = self._da
        attributes['operating_result']              = operating_result

@dataclasses.dataclass(init=True, frozen=True)
class IndustrialDRE(Balance):
    net_revenue: decimal.Decimal
    """Receita Líquida"""
    
    cost_of_goods_sold: decimal.Decimal
    """Custos das Mercadorias Vendidas (COGS)"""
    
    gross_profit: decimal.Decimal
    """Lucro Bruto"""
    
    operating_revenue_and_expenses: decimal.Decimal
    """Receitas e Despesas Operacionais"""
    
    operating_result: typing.Optional[decimal.Decimal]
    """Resultado Operacional (EBITDA)"""
    
    depreciation_and_amortization: typing.Optional[decimal.Decimal]
    """Depreciação e Amortização"""
    
    operating_profit: decimal.Decimal
    """Lucro Operacional (EBIT)"""
    
    financial_result: decimal.Decimal
    """Resultado Financeiro"""
    
    earnings_before_tax: decimal.Decimal
    """Resultado Antes dos Tributos sobre o Lucro (EBT)"""
    
    tax_expenses: decimal.Decimal
    """Imposto de Renda e Contribuição Social sobre o Lucro"""
    
    continuing_operation_result: decimal.Decimal
    """Resultado Líquido das Operações Continuadas"""
    
    discontinued_operation_result: decimal.Decimal
    """Resultado Líquido das Operações Descontinuadas"""
    
    net_profit: decimal.Decimal
    """Lucro Líquido"""

    @property
    def ebitda(self) -> typing.Optional[decimal.Decimal]:
        return self.operating_result

    @property
    def ebit(self) -> decimal.Decimal:
        return self.operating_profit

    @property
    def ebt(self) -> decimal.Decimal:
        return self.earnings_before_tax

    __layout__ = (
        ('3.01', 'Receita de Venda de Bens e/ou Serviços',                 'net_revenue'),
        ('3.02', 'Custo dos Bens e/ou Serviços Vendidos',                  'cost_of_goods_sold'),
        ('3.03', 'Resultado Bruto',                                        'gross_profit'),
        ('3.04', 'Despesas/Receitas Operacionais',                         'operating_revenue_and_expenses'),
        ('3.05', 'Resultado Antes do Resultado Financeiro e dos Tributos', 'operating_profit'),
        ('3.06', 'Resultado Financeiro',                                   'financial_result'),
        ('3.07', 'Resultado Antes dos Tributos sobre o Lucro',             'earnings_before_tax'),
        ('3.08', 'Imposto de Renda e Contribuição Social sobre o Lucro',   'tax_expenses'),
        ('3.09', 'Resultado Líquido das Operações Continuadas',            'continuing_operation_result'),
        ('3.10', 'Resultado Líquido de Operações Descontinuadas',          'discontinued_operation_result'),
        ('3.11', 'Lucro/Prejuízo do Período',                              'net_profit'),
    )

    __parser__ = IndustrialDREParser

    __slots__ = (
        'net_revenue',
        'cost_of_goods_sold',
        'gross_profit',
        'operating_revenue_and_expenses',
        'operating_result',
        'depreciation_and_amortization',
        'operating_profit',
        'financial_result',
        'earnings_before_tax',
        'tax_expenses',
        'continuing_operation_result',
        'discontinued_operation_result',
        'net_profit'
    )

    def validate(self):
        # TODO
        pass
