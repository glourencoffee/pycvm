import csv
import zlib
from datetime           import date
from cvm.datatypes.cnpj import CNPJ
from cvm.parsing.csvrow import CsvRow
from cvm.parsing.util   import date_from_string, date_to_string

def element_group_id(cnpj: CNPJ, reference_date: date, version: int) -> int:
    """Returns the hash id identifying an element's group.
    
    A DFP file row has at least the following three fields:
    1. CNPJ;
    2. Reference date;
    3. Version.

    These fields are used to generate a hash id that identifies a row's group,
    allowing that row to be used to create a new element or to be aggregated
    into an existing element.

    This wouldn't be necessary if all CSV statements files had a field 'ID_DOC',
    which only exists in the main CSV file. But I wasn't the one to decide how
    to structure the files, so generating a group id is the way.
    """

    hash_str = str(int(cnpj)) + date_to_string(reference_date) + str(version)

    return zlib.crc32(hash_str.encode('utf-8'))

class Element:
    """Stores the three document-identifying fields of statement CSV files."""

    cnpj: CNPJ
    reference_date: date
    version: int

    def __init__(self, cnpj: CNPJ, reference_date: date, version: int):
        self.cnpj           = cnpj
        self.reference_date = reference_date
        self.version        = version

    def group_id(self) -> int:
        return element_group_id(self.cnpj, self.reference_date, self.version)

class ElementReader:
    __elemtype__ = Element

    __slots__ = ['_csv_dick_reader', '_cached_row_data']

    def __init__(self, file):
        # Yes, "dick" reader, just for fun.
        self._csv_dick_reader = csv.DictReader(file, delimiter=';')
        self._cached_row_data = None

    def read(self, elem: __elemtype__, row: CsvRow):
        pass

    def __iter__(self):
        return self

    def __next__(self) -> __elemtype__:
        if self._cached_row_data is None:
            elem = None
        else:
            cnpj, reference_date, version, row = self._cached_row_data
            elem = self.__elemtype__(cnpj, reference_date, version)

            self.read(elem, row)

        for row in self._csv_dick_reader:
            row            = CsvRow(row)
            cnpj           = row.required('CNPJ_CIA', CNPJ)
            reference_date = row.required('DT_REFER', date_from_string)
            version        = row.required('VERSAO',   int)

            curr_group_id = element_group_id(cnpj, reference_date, version)

            if elem is None:
                # No element is being read, so create one and read it.
                elem = self.__elemtype__(cnpj, reference_date, version)
                self.read(elem, row)

            elif elem.group_id() == curr_group_id:
                # Got a row of same group as the current element. Read row into element.
                self.read(elem, row)

            else:
                # Got a row of a different group from the current element. Cache up
                # row data for a follow-up call to this method. Return element.
                self._cached_row_data = (cnpj, reference_date, version, row)
                return elem

        if elem is not None:
            return elem
        
        raise StopIteration()