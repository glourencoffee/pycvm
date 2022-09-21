from __future__ import annotations
import dataclasses
import datetime
import typing
from cvm                         import datatypes, exceptions
from cvm.balances.industrial.dre import IndustrialDREValidator
from cvm.balances.financial.dre  import FinancialDREValidator
from cvm.balances.insurance.dre  import InsuranceDREValidator
from cvm.balances.account_layout import AccountLayoutType

__all__ = [
    'IncomeStatement'
]

@dataclasses.dataclass(init=True)
class IncomeStatement:
    revenue: int
    """Receita"""

    costs: int
    """Custos"""

    gross_profit: int
    """Lucro Bruto (Resultado Bruto)"""
    
    operating_income_and_expenses: int
    """Receitas e Despesas Operacionais"""

    operating_result: typing.Optional[int]
    """Resultado Operacional (EBITDA)"""
    
    depreciation_and_amortization: typing.Optional[int]
    """Depreciação e Amortização"""
    
    operating_profit: int
    """Lucro Operacional (EBIT)"""

    nonoperating_result: int
    """Resultado Não-Operacional (Resultado Financeiro)"""
    
    earnings_before_tax: int
    """Resultado Antes dos Tributos sobre o Lucro (EBT)"""
    
    tax_expenses: int
    """Imposto de Renda e Contribuição Social sobre o Lucro"""
    
    continuing_operation_result: int
    """Resultado Líquido das Operações Continuadas"""
    
    discontinued_operation_result: int
    """Resultado Líquido das Operações Descontinuadas"""
    
    net_income: int
    """Lucro Líquido"""

    @property
    def ebitda(self) -> typing.Optional[int]:
        """Alias to `operating_result`."""

        return self.operating_result

    @property
    def ebit(self) -> int:
        """Alias to `operating_profit`."""

        return self.operating_profit

    @property
    def ebt(self) -> int:
        """Alias to `earnings_before_tax`."""

        return self.earnings_before_tax

    __slots__ = (
        'revenue',
        'costs',
        'gross_profit',
        'operating_income_and_expenses',
        'operating_result',
        'depreciation_and_amortization',
        'operating_profit',
        'nonoperating_result',
        'earnings_before_tax',
        'tax_expenses',
        'continuing_operation_result',
        'discontinued_operation_result',
        'net_income'
    )

    @classmethod
    def from_accounts(cls,
                      layout_type: AccountLayoutType,
                      dre_accounts: typing.Sequence[datatypes.Account],
                      balance_type: datatypes.BalanceType,
                      reference_date: datetime.date
    ) -> IncomeStatement:
        if layout_type == AccountLayoutType.INDUSTRIAL:
            dre_validator = IndustrialDREValidator()

        elif layout_type == AccountLayoutType.FINANCIAL:
            dre_validator = FinancialDREValidator()
        
        elif layout_type == AccountLayoutType.INSURANCE:
            dre_validator = InsuranceDREValidator()

        else:
            raise ValueError(f'invalid AccountLayoutType {layout_type}')
        
        try:
            attrs = dre_validator.validate(dre_accounts, balance_type, reference_date)
        except exceptions.AccountLayoutError as exc:
            raise exceptions.AccountLayoutError(f'{dre_validator.__class__.__name__} error: {exc}') from None
        else:
            return cls(**attrs)

    @classmethod
    def from_collection(cls,
                        layout_type: AccountLayoutType,
                        collection: datatypes.StatementCollection,
                        reference_date: datetime.date
    ) -> IncomeStatement:
        return cls.from_accounts(
            layout_type,
            collection.dre.normalized().accounts,
            collection.balance_type,
            reference_date
        )

    @classmethod
    def from_dfpitr(cls,
                    dfpitr: datatypes.DFPITR,
                    balance_type: datatypes.BalanceType = datatypes.BalanceType.CONSOLIDATED,
                    fiscal_year_order: datatypes.FiscalYearOrder = datatypes.FiscalYearOrder.LAST
    ) -> IncomeStatement:
        grouped_collection = dfpitr[balance_type]

        if grouped_collection is None:
            raise ValueError(f'{dfpitr} does not have a grouped collection for balance type {balance_type}')

        return cls.from_collection(
            AccountLayoutType.from_cvm_code(dfpitr.cvm_code),
            grouped_collection[fiscal_year_order],
            dfpitr.reference_date
        )