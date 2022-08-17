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
from cvm.exceptions import NotImplementedException, BalanceLayoutError

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
    def from_statements(cls, collection: statement.StatementCollection, balance_type: statement.BalanceType) -> BalanceCollection:
        raise NotImplementedException(cls, 'from_statements')

@dataclasses.dataclass(init=True, frozen=True)
class IndustrialCollection:
    bpa: m_bpa.IndustrialBPA
    bpp: m_bpp.IndustrialBPP
    dre: m_dre.IndustrialDRE

    @classmethod
    def from_statements(cls, collection: statement.StatementCollection, balance_type: statement.BalanceType) -> IndustrialCollection:
        return IndustrialCollection(
            bpa = balance.make_balance(m_bpa.IndustrialBPA, collection.bpa.accounts, balance_type),
            bpp = balance.make_balance(m_bpp.IndustrialBPP, collection.bpp.accounts, balance_type),
            dre = balance.make_balance(m_dre.IndustrialDRE, collection.dre.accounts, balance_type)
        )

def make_balance_collection(collection: statement.StatementCollection, balance_type: statement.BalanceType) -> BalanceCollection:
    for cls in (IndustrialCollection,):
        try:
            industrial = cls.from_statements(statements, balance_type)
        except BalanceLayoutError:
            continue
    
    raise BalanceLayoutError('statement collection doesnt match any balance collection')