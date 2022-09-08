import dataclasses
import datetime
import typing
from cvm import datatypes

__all__ = [
    'DocumentType',
    'RegularDocument',
    'FCA',
    'DFPITR'
]

class DocumentType(datatypes.DescriptiveIntEnum):
    FCA = (0, 'Formulário Cadastral')
    DFP = (1, 'Demonstrações Fiscais Padronizadas')
    ITR = (2, 'Informe Trimestral')

@dataclasses.dataclass(init=True, repr=False)
class RegularDocument:
    """A regular document is a structured document specified by a CVM Instruction.
    
    Not all documents are regular; some are sent by companies without any structure,
    having the sole purpose of notifying investors.

    This class implements the attributes that are common to all regular documents.
    """

    cnpj: datatypes.CNPJ
    reference_date: datetime.date
    version: int
    company_name: str
    cvm_code: str
    type: DocumentType
    id: int
    receipt_date: datetime.date
    url: str

    def __repr__(self) -> str:
        return f'<RegularDocument: id={self.id} type={self.type} version={self.version} CNPJ={self.cnpj}>'

@dataclasses.dataclass(init=True, repr=False)
class FCA(RegularDocument):
    """A Registration Form ("Formulário Cadastral" or "FCA") is a regular document
    that open-market companies are required to send to CVM. It is specified by the
    CVM Instruction 480/2009, which is found at the CVM offical website[1].

    This class implements the data structure specified by the Instruction by
    separating each Item in the Instruction to a class attribute.
    
    [1] https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/instrucoes/anexos/400/inst480consolid.pdf ("Anexo 22")
    """

    issuer_company: typing.Optional[datatypes.IssuerCompany]
    """Instruction Item 1"""

    securities: typing.Tuple[datatypes.Security]
    """Instruction Item 2"""

    auditors: typing.Tuple[datatypes.Auditor]
    """Instruction Item 3"""

    bookkeeping_agents: typing.Tuple[datatypes.BookkeepingAgent]
    """Instruction Item 4"""
    
    investor_relations_department: typing.Tuple[datatypes.InvestorRelationsOfficer]
    """Instruction Item 5"""

    shareholder_department: typing.Tuple[datatypes.ShareholderDepartmentPerson]
    """Instruction Item 6"""

@dataclasses.dataclass(init=True, repr=False)
class DFPITR(RegularDocument):
    """Implements the financial statement documents of Instruction CVM 480/2009.
    
    There are two types of financial statement documents:
    1. Standardized Financial Statements ("Demonstrações Fiscais Padronizadas" or "DFP")
    2. Quarterly Report ("Informe Trimestral" or "ITR")

    Both of them have the same data structure, with their difference being only the
    financial period covered. The first document contains data of a company's previous
    fiscal year, that is, it's an annual report, whereas the second contains data
    of a company's last quarter.
    
    As such, this class is named after both of them. To disambiguate between the
    two types of document, use the attribute `RegularDocument.type`.
    """

    individual: typing.Optional[datatypes.GroupedStatementCollection]
    consolidated: typing.Optional[datatypes.GroupedStatementCollection]

    def grouped_collections(self) -> typing.Generator[datatypes.GroupedStatementCollection, None, None]:
        return (coll for coll in (self.individual, self.consolidated) if coll is not None)

    def grouped_collection(self, balance_type: datatypes.BalanceType) -> typing.Optional[datatypes.GroupedStatementCollection]:
        if balance_type == datatypes.BalanceType.CONSOLIDATED:
            return self.consolidated
        else:
            return self.individual

    def __getitem__(self, balance_type: datatypes.BalanceType) -> typing.Optional[datatypes.GroupedStatementCollection]:
        return self.grouped_collection(balance_type)