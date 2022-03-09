import csv
import typing
from cvm.datatypes.tax_id   import CNPJ
from cvm.datatypes.document import RegularDocument, DocumentType
from cvm.csvio.row          import CSVRow
from cvm.csvio.batch        import CSVBatch, CSVBatchReader
from cvm.utils              import date_from_string

class RegularDocumentHeadReader:
    def __init__(self, file, delimiter: str = ';'):
        self._dict_reader = csv.DictReader(file, delimiter=delimiter)

    def read(self) -> RegularDocument:
        row = next(self._dict_reader)
        row = CSVRow(row)

        strtype = row.required('CATEG_DOC', str)
        doctype = None

        for dt in DocumentType:
            if dt.name == strtype:
                doctype = dt
                break

        if doctype is None:
            # TODO
            ...

        return RegularDocument(
            cnpj           = row.required('CNPJ_CIA',  CNPJ),
            reference_date = row.required('DT_REFER',  date_from_string),
            version        = row.required('VERSAO',    int),
            company_name   = row.required('DENOM_CIA', str),
            cvm_code       = row.required('CD_CVM',    int),
            type           = doctype,
            id             = row.required('ID_DOC',    int),
            receipt_date   = row.required('DT_RECEB',  date_from_string),
            url            = row.required('LINK_DOC',  str),
        )

class UnexpectedBatch(Exception):
    pass

class RegularDocumentBodyReader(CSVBatchReader):
    def __init__(self, file, delimiter: str = ';'):
        super().__init__(file, delimiter)

        self._cached_batch: typing.Optional[CSVBatch] = None

    def read_expected_batch(self, expected_batch_id: int) -> CSVBatch:
        if self._cached_batch is None:
            batch = self.read_batch()
        else:
            batch = self._cached_batch
            self._cached_batch = None

        if batch.id == expected_batch_id:
            return batch
        else:
            self._cached_batch = batch
            raise UnexpectedBatch()