from cvm.parsing.dfp.balance import Balance

class Balance(Balance):
    net_income: float
    """Receita Líquida"""
    
    cost_of_goods_sold: float
    """Custos das Mercadorias Vendidas (COGS)"""
    
    gross_profit: float
    """Lucro Bruto"""
    
    operating_revenue_and_expenses: float
    """Receitas e Despesas Operacionais"""
    
    operating_result: float
    """Resultado Operacional (EBITDA)"""
    
    depreciation_and_amortization: float
    """Depreciação e Amortização"""
    
    operating_profit: float
    """Lucro Operacional (EBIT)"""
    
    financial_result: float
    """Resultado Financeiro"""
    
    earnings_before_tax: float
    """Resultado Antes dos Tributos sobre o Lucro (EBT)"""
    
    tax_expenses: float
    """Imposto de Renda e Contribuição Social sobre o Lucro"""
    
    continuing_operation_results: float
    """Resultado Líquido das Operações Continuadas"""
    
    discontinued_operation_results: float
    """Resultado Líquido das Operações Descontinuadas"""
    
    net_profit: float
    """Lucro Líquido"""