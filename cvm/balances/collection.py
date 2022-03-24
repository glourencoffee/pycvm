from __future__ import annotations
import dataclasses
import typing
from cvm.balances import (
    balance,
    bpa as m_bpa,
    bpp as m_bpp,
    dre as m_dre
)
from cvm.datatypes  import document, statement
from cvm.exceptions import NotImplementedException

class BalanceCollection:
    @classmethod
    def from_document(cls, 
                      doc: document.DFPITR,
                      individual: bool,
                      fiscar_year_order: statement.FiscalYearOrder = statement.FiscalYearOrder.LAST
    ) -> BalanceCollection:
        
        if individual:
            stmts = doc.individual[fiscar_year_order]
        else:
            stmts = doc.consolidated[fiscar_year_order]

        return cls.from_statements(stmts)

    @classmethod
    def from_statements(cls, collection: statement.StatementCollection, is_individual: bool) -> BalanceCollection:
        raise NotImplementedException(cls, 'from_statements')

@dataclasses.dataclass(init=True, frozen=True)
class IndustrialCollection:
    bpa: m_bpa.IndustrialBPA
    bpp: m_bpp.IndustrialBPP
    dre: m_dre.IndustrialDRE

    @classmethod
    def from_statements(cls, collection: statement.StatementCollection, is_individual: bool) -> IndustrialCollection:
        return IndustrialCollection(
            bpa = balance.make_balance(m_bpa.IndustrialBPA, collection.bpa.accounts, is_individual=is_individual),
            bpp = balance.make_balance(m_bpp.IndustrialBPP, collection.bpp.accounts, is_individual=is_individual),
            dre = balance.make_balance(m_dre.IndustrialDRE, collection.dre.accounts, is_individual=is_individual)
        )