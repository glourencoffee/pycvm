import dataclasses
import datetime
import typing
from cvm.datatypes.auditor                    import Auditor
from cvm.datatypes.bookkeeping_agent          import BookkeepingAgent
from cvm.datatypes.investor_relations_officer import InvestorRelationsOfficer
from cvm.datatypes.issuer                     import IssuerCompany
from cvm.datatypes.enums                      import DescriptiveIntEnum
from cvm.datatypes.security                   import Security
from cvm.datatypes.shareholder_department     import ShareholderDepartmentPerson
from cvm.datatypes.statement                  import FiscalYearOrder, StatementCollection
from cvm.datatypes.tax_id                     import CNPJ

class DocumentType(DescriptiveIntEnum):
    FCA       = (0, 'Formulário Cadastral')
    DFP       = (1, 'Demonstrações Fiscais Padronizadas')
    ITR       = (2, 'Informe Trimestral')

@dataclasses.dataclass(init=True, frozen=True)
class RegularDocument:
    """A regular document is a structured document specified by a CVM Instruction.
    
    Not all documents are regular; some are sent by companies without any structure,
    having the sole purpose of notifying investors.

    This class implements the attributes that are common to all regular documents.
    """

    cnpj: CNPJ
    reference_date: datetime.date
    version: int
    company_name: str
    cvm_code: int
    type: DocumentType
    id: int
    receipt_date: datetime.date
    url: str

@dataclasses.dataclass(init=True, frozen=True)
class FCA(RegularDocument):
    """A Registration Form ("Formulário Cadastral" or "FCA") is a regular document
    that open-market companies are required to send to CVM. It is specified by the
    CVM Instruction 480/2009, which is found at the CVM offical website[1].

    This class implements the data structure specified by the Instruction by
    separating each Item in the Instruction to a class attribute.
    
    [1] https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/instrucoes/anexos/400/inst480consolid.pdf ("Anexo 22")
    """

    issuer_company: typing.Optional[IssuerCompany]
    """Instruction Item 1"""

    securities: typing.Tuple[Security]
    """Instruction Item 2"""

    auditors: typing.Tuple[Auditor]
    """Instruction Item 3"""

    bookkeeping_agents: typing.Tuple[BookkeepingAgent]
    """Instruction Item 4"""
    
    investor_relations_department: typing.Tuple[InvestorRelationsOfficer]
    """Instruction Item 5"""

    shareholder_department: typing.Tuple[ShareholderDepartmentPerson]
    """Instruction Item 6"""


@dataclasses.dataclass(init=True, frozen=True)
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

    individual: typing.Mapping[FiscalYearOrder, StatementCollection]
    consolidated: typing.Mapping[FiscalYearOrder, StatementCollection]