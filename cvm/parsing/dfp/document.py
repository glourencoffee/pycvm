from typing                    import Optional
from datetime                  import date
from cvm.parsing.dfp.element   import Element, ElementReader
from cvm.parsing.dfp.statement import StatementCollection
from cvm.parsing.csvrow        import CsvRow
from cvm.parsing.util          import date_from_string

class Document(Element):
    corporate_name: str
    cvm_code: int
    id: int
    receipt_date: date
    url: str
    individual: Optional[StatementCollection]
    consolidated: Optional[StatementCollection]

    def __repr__(self) -> str:
        return f"<Document id={self.id} corporate_name='{self.corporate_name}' version={self.version} receipt_date={self.receipt_date}>"

class DocumentReader(ElementReader):
    __elemtype__ = Document

    def read(self, elem: Document, row: CsvRow):
        super().read(elem, row)

        elem.corporate_name = row.required('DENOM_CIA', str)
        elem.cvm_code       = row.required('CD_CVM',    int)
        elem.id             = row.required('ID_DOC',    int)
        elem.receipt_date   = row.required('DT_RECEB',  date_from_string)
        elem.url            = row.required('LINK_DOC',  str)
        elem.individual     = None
        elem.consolidated   = None