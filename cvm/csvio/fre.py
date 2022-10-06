from __future__ import annotations
import contextlib
import os
import typing
from decimal            import Decimal
from zipfile            import ZipFile
from cvm.utils          import open_zip_member_on_stack, date_from_string
from cvm.datatypes      import FRE, CapitalDistribution, PreferredShareType, PreferredShareDistribution
from cvm.exceptions     import BadDocument
from cvm.csvio.member   import MemberNameList
from cvm.csvio.row      import CSVRow
from cvm.csvio.document import RegularDocumentHeadReader, RegularDocumentBodyReader, UnexpectedBatch

__all__ = [
    'fre_reader',
    'FREFile'
]

class FREMemberNameList(MemberNameList):
    head: str
    capital_distribution: str
    preferred_shares: str

    @classmethod
    def attribute_mapping(cls) -> typing.Dict[str, str]:
        return {
            '':                                  'head',
            '_distribuicao_capital':             'capital_distribution',
            '_distribuicao_capital_classe_acao': 'preferred_shares',
        }

    __slots__ = (
        'head',
        'capital_distribution',
        'preferred_shares',
    )

class CommonReader(RegularDocumentBodyReader):
    def batch_id(self, row: CSVRow) -> int:
        return row.required('ID_Documento', int)

class PreferredSharesReader(CommonReader):
    @staticmethod
    def make_preferred_share_type(name: str) -> PreferredShareType:
        return getattr(PreferredShareType, name)

    @classmethod
    def read_preferred_shares(cls, row: CSVRow) -> typing.Tuple[PreferredShareType, PreferredShareDistribution]:
        preferred_share_type = row.required('Sigla_Classe_Acoes_Preferenciais', cls.make_preferred_share_type)
        preferred_share_dist = PreferredShareDistribution(
            count   = row.required('Quantidade_Acoes_Preferenciais_Circulacao', int),
            percent = row.required('Percentual_Acoes_Preferenciais_Circulacao', Decimal)
        )

        return preferred_share_type, preferred_share_dist

    def read(self, document_id: int) -> typing.Dict[PreferredShareType, PreferredShareDistribution]:
        batch            = self.read_expected_batch(document_id)
        preferred_shares = {}
        
        for row in batch:
            preferred_share_type, preferred_share_dist = self.read_preferred_shares(row)
            preferred_shares[preferred_share_type] = preferred_share_dist

        return preferred_shares

class CapitalDistributionReader(CommonReader):
    def read(self, document_id: int, preferred_shares: typing.Dict[PreferredShareType, PreferredShareDistribution]) -> CapitalDistribution:
        batch = self.read_expected_batch(document_id)
        row   = batch.rows[0]

        return CapitalDistribution(
            individual_shareholder_count         = row.required('Quantidade_Acionistas_PF',                          int),
            corporation_shareholder_count        = row.required('Quantidade_Acionistas_PJ',                          int),
            institutional_investor_count         = row.required('Quantidade_Acionistas_Investidores_Institucionais', int),
            outstanding_common_shares_count      = row.required('Quantidade_Acoes_Ordinarias_Circulacao',            int),
            outstanding_common_shares_percent    = row.required('Percentual_Acoes_Ordinarias_Circulacao',            Decimal),
            outstanding_preferred_shares_count   = row.required('Quantidade_Acoes_Preferenciais_Circulacao',         int),
            outstanding_preferred_shares_percent = row.required('Percentual_Acoes_Preferenciais_Circulacao',         Decimal),
            outstanding_preferred_shares         = preferred_shares,
            outstanding_shares_count             = row.required('Quantidade_Total_Acoes_Circulacao',                 int),
            outstanding_shares_percent           = row.required('Percentual_Total_Acoes_Circulacao',                 Decimal),
            last_shareholder_meeting_date        = row.required('Data_Ultima_Assembleia',                            date_from_string),
        )

def _reader(archive: ZipFile, namelist: FREMemberNameList) -> typing.Generator[FRE, None, None]:
    with contextlib.ExitStack() as stack:
        head_reader             = RegularDocumentHeadReader(open_zip_member_on_stack(stack, archive, namelist.head))
        capital_dist_reader     = CapitalDistributionReader(open_zip_member_on_stack(stack, archive, namelist.capital_distribution))
        preferred_shares_reader = PreferredSharesReader(open_zip_member_on_stack(stack, archive, namelist.preferred_shares))

        while True:
            try:
                head = head_reader.read()
            except StopIteration:
                break

            try:
                preferred_shares = preferred_shares_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                preferred_shares = {}
            except BadDocument as exc:
                print('Error while reading preferred share distribution:', exc)
                preferred_shares = {}

            try:
                capital_dist = capital_dist_reader.read(head.id, preferred_shares)
            except (UnexpectedBatch, StopIteration):
                capital_dist = None
            except BadDocument as exc:
                print('Error while reading capital distribution:', exc)
                capital_dist = None

            yield FRE(
                cnpj                          = head.cnpj,
                reference_date                = head.reference_date,
                version                       = head.version,
                company_name                  = head.company_name,
                cvm_code                      = head.cvm_code,
                type                          = head.type,
                id                            = head.id,
                receipt_date                  = head.receipt_date,
                url                           = head.url,
                capital_distribution          = capital_dist
            )

def fre_reader(archive: ZipFile) -> typing.Generator[FRE, None, None]:
    namelist = FREMemberNameList(iter(archive.namelist()))

    return _reader(archive, namelist)

class FREFile(ZipFile):
    """Class for reading `DFPITR` objects from a DFP/ITR file."""

    def __init__(self, file: typing.Union[os.PathLike, typing.IO[bytes]]) -> None:
        """Opens the DFP/ITR file in read mode."""

        super().__init__(file, mode='r')

        self._reader = fre_reader(archive=self)

    def __iter__(self) -> FREFile:
        return self

    def __next__(self) -> FRE:
        return next(self._reader)