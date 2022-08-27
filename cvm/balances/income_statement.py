from __future__ import annotations
import dataclasses
import datetime
import typing
from cvm                         import datatypes, exceptions
from cvm.balances.industrial.dre import IndustrialDREValidator
from cvm.balances.financial.dre  import FinancialDREValidator
from cvm.balances.insurance.dre  import InsuranceDREValidator

__validators__ = (
    IndustrialDREValidator,
    FinancialDREValidator,
    InsuranceDREValidator
)

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
                      dre_accounts: datatypes.AccountTuple,
                      balance_type: datatypes.BalanceType,
                      reference_date: datetime.date
    ) -> IncomeStatement:
        error_strings = []

        for dre_validator in __validators__:
            try:
                attrs = dre_validator().validate(dre_accounts.normalized(), balance_type, reference_date)
            except exceptions.AccountLayoutError as exc:
                error_strings.append(f'{dre_validator.__name__}: {exc}')
                continue
            else:
                return cls(**attrs)
        
        raise exceptions.AccountLayoutError(f'invalid DRE: {error_strings}')

    @classmethod
    def from_collection(cls,
                        collection: datatypes.StatementCollection,
                        balance_type: datatypes.BalanceType,
                        reference_date: datetime.date
    ) -> IncomeStatement:
        return cls.from_accounts(
            collection.dre.accounts,
            balance_type,
            reference_date
        )

    @classmethod
    def from_document(cls,
                      document: datatypes.DFPITR,
                      balance_type: datatypes.BalanceType = datatypes.BalanceType.CONSOLIDATED
    ) -> IncomeStatement:
        mapping    = document[balance_type]
        collection = mapping[datatypes.FiscalYearOrder.LAST]

        return cls.from_collection(
            collection,
            balance_type,
            document.reference_date
        )