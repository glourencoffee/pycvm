from __future__ import annotations
import dataclasses
import datetime
import functools
import typing
from cvm.balances.industrial.bpa import IndustrialBPAValidator
from cvm.balances.industrial.bpp import IndustrialBPPValidator
from cvm.balances.financial.bpa  import FinancialBPAValidator
from cvm.balances.financial.bpp  import FinancialBPPValidator
from cvm.balances.insurance.bpa  import InsuranceBPAValidator
from cvm.balances.insurance.bpp  import InsuranceBPPValidator
from cvm.balances.account_layout import AccountLayoutType
from cvm                         import datatypes, exceptions

__all__ = [
    'BalanceSheet'
]

@dataclasses.dataclass(init=True)
class BalanceSheet:
    """TODO"""

    total_assets: int
    current_assets: typing.Optional[int]
    cash_and_cash_equivalents: int
    financial_investments: int
    receivables: int
    noncurrent_assets: typing.Optional[int]
    investments: int
    fixed_assets: int
    intangible_assets: int

    total_liabilities: int
    current_liabilities: typing.Optional[int]
    current_loans_and_financing: typing.Optional[int]
    noncurrent_liabilities: typing.Optional[int]
    noncurrent_loans_and_financing: typing.Optional[int]

    equity: int

    @functools.cached_property
    def gross_debt(self) -> typing.Optional[int]:
        try:
            return abs(self.current_loans_and_financing + self.noncurrent_loans_and_financing)
        except TypeError:
            return None

    @functools.cached_property
    def net_debt(self) -> typing.Optional[int]:
        try:
            return self.gross_debt - self.cash_and_cash_equivalents
        except TypeError:
            return None

    @classmethod
    def from_accounts(cls,
                      layout_type: AccountLayoutType,
                      bpa_accounts: typing.Sequence[datatypes.Account],
                      bpp_accounts: typing.Sequence[datatypes.Account],
                      balance_type: datatypes.BalanceType,
                      reference_date: datetime.date
    ) -> BalanceSheet:
        if layout_type == AccountLayoutType.INDUSTRIAL:
            bpa_validator = IndustrialBPAValidator()
            bpp_validator = IndustrialBPPValidator()

        elif layout_type == AccountLayoutType.FINANCIAL:
            bpa_validator = FinancialBPAValidator()
            bpp_validator = FinancialBPPValidator()
        
        elif layout_type == AccountLayoutType.INSURANCE:
            bpa_validator = InsuranceBPAValidator()
            bpp_validator = InsuranceBPPValidator()
        
        else:
            raise ValueError(f'invalid AccountLayoutType {layout_type}')

        bpa_attrs = {}
        bpp_attrs = {}

        try:
            bpa_attrs = bpa_validator.validate(bpa_accounts, balance_type, reference_date)
        except exceptions.AccountLayoutError as exc:
            raise exceptions.AccountLayoutError(f'{bpa_validator.__class__.__name__} error: {exc}') from None
            
        try:
            bpp_attrs = bpp_validator.validate(bpp_accounts, balance_type, reference_date)
        except  exceptions.AccountLayoutError as exc:
            raise exceptions.AccountLayoutError(f'{bpp_validator.__class__.__name__} error: {exc}') from None

        return cls(**bpa_attrs, **bpp_attrs)

    @classmethod
    def from_collection(cls,
                        layout_type: AccountLayoutType,
                        collection: datatypes.StatementCollection,
                        reference_date: datetime.date
    ) -> BalanceSheet:
        return cls.from_accounts(
            layout_type,
            collection.bpa.normalized().accounts,
            collection.bpp.normalized().accounts,
            collection.balance_type,
            reference_date
        )

    @classmethod
    def from_dfpitr(cls,
                    dfpitr: datatypes.DFPITR,
                    balance_type: datatypes.BalanceType = datatypes.BalanceType.CONSOLIDATED,
                    fiscal_year_order: datatypes.FiscalYearOrder = datatypes.FiscalYearOrder.LAST
    ) -> BalanceSheet:
        grouped_collection = dfpitr[balance_type]

        if grouped_collection is None:
            raise ValueError(f'{dfpitr} does not have a grouped collection for balance type {balance_type}')

        return cls.from_collection(
            AccountLayoutType.from_cvm_code(dfpitr.cvm_code),
            grouped_collection[fiscal_year_order],
            dfpitr.reference_date
        )