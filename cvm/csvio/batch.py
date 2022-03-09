import dataclasses
import typing
import csv
from cvm.csvio.row  import CSVRow
from cvm.exceptions import NotImplementedException

@dataclasses.dataclass(init=True, frozen=False)
class CSVBatch:
    """Collects CSV rows that have been identified as part of a same group."""

    id: int
    rows: typing.List[CSVRow] = dataclasses.field(default_factory=list)

    def __iter__(self):
        return iter(self.rows)

class CSVBatchReader:
    """Reads CSV batches."""

    __slots__ = ('_dict_reader', '_cached_row')

    def __init__(self, file, delimiter: str = ';'):
        self._dict_reader = csv.DictReader(file, delimiter=delimiter)
        self._cached_row  = None

    def batch_id(self, row: CSVRow) -> int:
        raise NotImplementedException(self.__class__, 'batch_id')

    def read_batch(self) -> CSVBatch:
        if self._cached_row is None:
            first_row = CSVRow(next(self._dict_reader))
        else:
            first_row        = self._cached_row
            self._cached_row = None

        batch = CSVBatch(self.batch_id(first_row))
        batch.rows.append(first_row)

        for row in self._dict_reader:
            row      = CSVRow(row)
            batch_id = self.batch_id(row)

            if batch_id == batch.id:
                batch.rows.append(row)
            else:
                self._cached_row = row
                return batch