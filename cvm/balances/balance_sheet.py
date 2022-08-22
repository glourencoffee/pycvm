from __future__ import annotations
import dataclasses
import functools
import typing
from cvm.balances.industrial.bpa import IndustrialBPAValidator
from cvm.balances.industrial.bpp import IndustrialBPPValidator
from cvm.balances.financial.bpa  import FinancialBPAValidator
from cvm.balances.financial.bpp  import FinancialBPPValidator
from cvm                         import datatypes, exceptions

__validator_pairs__ = (
    (IndustrialBPAValidator, IndustrialBPPValidator),
    (FinancialBPAValidator,  FinancialBPPValidator),
)

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
    def from_document(cls, document: datatypes.DFPITR, balance_type: datatypes.BalanceType = datatypes.BalanceType.CONSOLIDATED, **kwargs):
        stmts     = document[balance_type][datatypes.FiscalYearOrder.LAST]
        bpa_attrs = {}
        bpp_attrs = {}
        error_str = []

        for bpa_validator, bpp_validator in __validator_pairs__:
            try:
                bpa_attrs = bpa_validator().validate(stmts.bpa.accounts.normalized(), balance_type, document.reference_date)
            except exceptions.AccountLayoutError as exc:
                error_str.append(f'{bpa_validator.__name__}: {exc}')
                continue
            
            try:
                bpp_attrs = bpp_validator().validate(stmts.bpp.accounts.normalized(), balance_type, document.reference_date)
            except  exceptions.AccountLayoutError as exc:
                error_str.append(f'{bpp_validator.__name__}: {exc}')
                continue
            else:
                return cls(**bpa_attrs, **bpp_attrs, **kwargs)
        
        raise exceptions.AccountLayoutError(f'invalid BPA or BPP: {error_str}')