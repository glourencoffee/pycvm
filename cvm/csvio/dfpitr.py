import collections
import contextlib
import datetime
import decimal
import enum
import io
import os
import typing
import zipfile
import zlib
from cvm import datatypes
from cvm.csvio.batch import CSVBatch
from cvm.csvio.document      import RegularDocumentHeadReader, RegularDocumentBodyReader, UnexpectedBatch
from cvm.csvio.row           import CSVRow
from cvm.datatypes.account   import Account, AccountTuple
from cvm.datatypes.currency  import Currency, CurrencySize
from cvm.datatypes.tax_id    import CNPJ
from cvm.datatypes.statement import GroupedStatementCollection, StatementType, Statement, DFCMethod, FiscalYearOrder, BPx, DRxDVA, DFC, DMPL
from cvm.datatypes.document  import DFPITR
from cvm.exceptions          import ZipMemberError, NotImplementedException, InvalidValueError, BadDocument
from cvm.utils               import date_from_string

class _MemberNameList:
    head_filename: str
    con_filenames: typing.Dict[StatementType, str]
    ind_filenames: typing.Dict[StatementType, str]

    def __init__(self, namelist: typing.Iterable[str]):
        self.head_filename = ''
        self.con_filenames = {}
        self.ind_filenames = {}

        # <file-name>   ::= <prefix> <middle-name> <suffix>
        # <prefix>      ::= ("dfp" | "itr") "_cia_aberta" ["_"]
        # <middle-name> ::= see below
        # <suffix>      ::= "_" <4-digit-year> ".csv"
        prefix_length = len('XXX_cia_aberta')
        suffix_length = len('_XXXX.csv')

        for name in namelist:
            try:
                middle_name = name[prefix_length:-suffix_length]
            except IndexError:
                raise ZipMemberError(name)

            if   middle_name == '':            self.head_filename                       = name
            elif middle_name == '_BPA_con':    self.con_filenames[StatementType.BPA]    = name
            elif middle_name == '_BPA_ind':    self.ind_filenames[StatementType.BPA]    = name
            elif middle_name == '_BPP_con':    self.con_filenames[StatementType.BPP]    = name
            elif middle_name == '_BPP_ind':    self.ind_filenames[StatementType.BPP]    = name
            elif middle_name == '_DFC_MD_con': self.con_filenames[StatementType.DFC_MD] = name
            elif middle_name == '_DFC_MD_ind': self.ind_filenames[StatementType.DFC_MD] = name
            elif middle_name == '_DFC_MI_con': self.con_filenames[StatementType.DFC_MI] = name
            elif middle_name == '_DFC_MI_ind': self.ind_filenames[StatementType.DFC_MI] = name
            elif middle_name == '_DMPL_con':   self.con_filenames[StatementType.DMPL]   = name
            elif middle_name == '_DMPL_ind':   self.ind_filenames[StatementType.DMPL]   = name
            elif middle_name == '_DRA_con':    self.con_filenames[StatementType.DRA]    = name
            elif middle_name == '_DRA_ind':    self.ind_filenames[StatementType.DRA]    = name
            elif middle_name == '_DRE_con':    self.con_filenames[StatementType.DRE]    = name
            elif middle_name == '_DRE_ind':    self.ind_filenames[StatementType.DRE]    = name
            elif middle_name == '_DVA_con':    self.con_filenames[StatementType.DVA]    = name
            elif middle_name == '_DVA_ind':    self.ind_filenames[StatementType.DVA]    = name
            else:
                raise ZipMemberError(name)

def _row_batch_id(cnpj: CNPJ, reference_date: datetime.date, version: int) -> int:
    """Calculates the row batch id of a DFP file based on the value of repeated fields.
    
    A CSV file of a DFP file has at least three fields:
    1. CNPJ;
    2. Reference date;
    3. Version.

    These fields are repeated for rows of a same DFP document.
    
    Unlike with FCA files, which have a field `ID_Documento`, DFP statement
    files don't have such a field. So, what we do is to calculate a hash id
    from the three repeated fields and use it as a row batch id.
    """

    hash_str = cnpj.to_string(use_separator=False) + str(reference_date) + str(version)

    return zlib.crc32(hash_str.encode('utf-8'))

class StatementReader(RegularDocumentBodyReader):
    def batch_id(self, row: CSVRow) -> int:
        cnpj           = row.required('CNPJ_CIA', CNPJ.from_zfilled_with_separators)
        reference_date = row.required('DT_REFER', date_from_string)
        version        = row.required('VERSAO',   int)

        return _row_batch_id(cnpj, reference_date, version)

    def read(self, expected_batch_id: int):
        batch = self.read_expected_batch(expected_batch_id)
        stmts = self.read_statements(batch)

        return stmts

    def read_common(self, row: CSVRow) -> typing.Tuple[Currency, CurrencySize, datetime.date]:
        return (
            row.required('MOEDA',        Currency),
            row.required('ESCALA_MOEDA', CurrencySize)
        )

    def read_account(self, row: CSVRow) -> Account:
        return Account(
            code      = row.required('CD_CONTA',      str),
            name      = row.optional('DS_CONTA',      str),
            quantity  = row.required('VL_CONTA',      decimal.Decimal),
            is_fixed  = row.required('ST_CONTA_FIXA', str) == 'S'
        )

    def read_accounts(self, rows: typing.List[CSVRow]) -> AccountTuple:
        currency, currency_size = self.read_common(rows[0])
        accounts = AccountTuple(currency, currency_size, (self.read_account(row) for row in rows))

        return accounts

    def read_statements(self, batch: CSVBatch) -> typing.List[typing.Any]:
        grouped_rows = collections.defaultdict(list)

        for row in batch:
            key = self.read_group_key(row)
            grouped_rows[key].append(row)

        statements = []

        for key, rows in grouped_rows.items():
            statement = self.create_statement(rows)
            statements.append(statement)

        return statements

    def read_group_key(self, row: CSVRow) -> str:
        key = ''

        for fieldname in self.group_key_fields():
            key += row.required(fieldname, str)

        return key

    def group_key_fields(self) -> typing.Sequence[str]:
        raise NotImplementedException(self.__class__, 'group_key_fields')

    def create_statement(self, rows: typing.List[CSVRow]) -> Statement:
        raise NotImplementedException(self.__class__, 'create_statement')

class BPxReader(StatementReader):
    def group_key_fields(self) -> typing.Sequence[str]:
        return ('ORDEM_EXERC', 'DT_FIM_EXERC')

    def create_statement(self, rows: typing.List[CSVRow]) -> BPx:
        first_row = rows[0]

        return BPx(
            fiscal_year_order = first_row.required('ORDEM_EXERC',  FiscalYearOrder),
            period_end_date   = first_row.required('DT_FIM_EXERC', date_from_string),
            accounts          = self.read_accounts(rows)
        )

class DRxDVAReader(StatementReader):
    def group_key_fields(self) -> typing.Sequence[str]:
        return ('ORDEM_EXERC', 'DT_INI_EXERC', 'DT_FIM_EXERC')

    def create_statement(self, rows: typing.List[CSVRow]) -> DRxDVA:
        first_row = rows[0]

        return DRxDVA(
            fiscal_year_order = first_row.required('ORDEM_EXERC',  FiscalYearOrder),
            period_start_date = first_row.required('DT_INI_EXERC', date_from_string),
            period_end_date   = first_row.required('DT_FIM_EXERC', date_from_string),
            accounts          = self.read_accounts(rows)
        )

class DFCReader(StatementReader):
    def group_key_fields(self) -> typing.Sequence[str]:
        return ('ORDEM_EXERC', 'DT_INI_EXERC', 'DT_FIM_EXERC')

    def create_statement(self, rows: typing.List[CSVRow]) -> DFC:
        first_row = rows[0]

        statement_name = first_row.required('GRUPO_DFP', str)

        try:
            # 'Demonstração de Fluxo de Caixa (Método Direto)' or
            # 'Demonstração de Fluxo de Caixa (Método Indireto)'
            dfc_method_name = statement_name.split('(')[1].rstrip(')')
        except IndexError:
            raise InvalidValueError(f"unexpected value '{statement_name}' at field 'GRUPO_DFP'") from None

        dfc_method = DFCMethod(dfc_method_name)

        return DFC(
            fiscal_year_order = first_row.required('ORDEM_EXERC',  FiscalYearOrder),
            method            = dfc_method,
            period_start_date = first_row.required('DT_INI_EXERC', date_from_string),
            period_end_date   = first_row.required('DT_FIM_EXERC', date_from_string),
            accounts          = self.read_accounts(rows)
        )

class DMPLReader(StatementReader):
    def group_key_fields(self) -> typing.Sequence[str]:
        return ('ORDEM_EXERC', 'DT_INI_EXERC', 'DT_FIM_EXERC')

    def create_statement(self, rows: typing.List[CSVRow]) -> DMPL:
        first_row = rows[0]

        columns_with_accounts = collections.defaultdict(list)

        for row in rows:
            column  = row.required('COLUNA_DF', str)
            account = self.read_account(row)
            
            columns_with_accounts[column].append(account)

        columns_with_account_tuple = {}

        currency, currency_size = self.read_common(first_row)

        for column, accounts in columns_with_accounts.items():
            columns_with_account_tuple[column] = AccountTuple(currency, currency_size, accounts)

        return DMPL(
            fiscal_year_order = first_row.required('ORDEM_EXERC',  FiscalYearOrder),
            period_start_date = first_row.required('DT_INI_EXERC', date_from_string),
            period_end_date   = first_row.required('DT_FIM_EXERC', date_from_string),
            columns           = columns_with_account_tuple
        )

class BalanceFlag(enum.IntFlag):
    NONE         = 0
    CONSOLIDATED = 1
    INDIVIDUAL   = 2

def _zip_reader(file: zipfile.ZipFile, flag: BalanceFlag) -> typing.Generator[DFPITR, None, None]:
    ################################################################################
    # The implementation below tries to read all the CSV files contained in the DFP
    # ZIP file simultaneously, taking advantage of the fact that data in these files
    # are structured according to the "main file." For example, the DFP of year 2020
    # (found in http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2020.zip)
    # has the following files:
    # - dfp_cia_aberta_2020.csv
    # - dfp_cia_aberta_BPA_con_2020.csv
    # - dfp_cia_aberta_BPA_ind_2020.csv
    # - dfp_cia_aberta_BPP_con_2020.csv
    # - dfp_cia_aberta_BPP_ind_2020.csv
    # - dfp_cia_aberta_DFC_MD_con_2020.csv
    # - dfp_cia_aberta_DFC_MD_ind_2020.csv
    # - dfp_cia_aberta_DFC_MI_con_2020.csv
    # - dfp_cia_aberta_DFC_MI_ind_2020.csv
    # - dfp_cia_aberta_DMPL_con_2020.csv
    # - dfp_cia_aberta_DMPL_ind_2020.csv
    # - dfp_cia_aberta_DRA_con_2020.csv
    # - dfp_cia_aberta_DRA_ind_2020.csv
    # - dfp_cia_aberta_DRE_con_2020.csv
    # - dfp_cia_aberta_DRE_ind_2020.csv
    # - dfp_cia_aberta_DVA_con_2020.csv
    # - dfp_cia_aberta_DVA_ind_2020.csv
    #
    # The first CSV in the above list is what I call the "head file." All other CSV
    # files are "statement files." Data in statement files are structured according
    # to the rows in the head file.
    # 
    # Every row in the head file results in a corresponding `DFPITR` document, which
    # will be yielded by this generator along with any statements the document has.
    #
    # All these files are read simultaneously. Why not open all CSV files, extract
    # their data, and *then* process everything? Well, every extracted ZIP file is
    # ~200 MB. It doesn't sound like a good idea to me to store 200 MB on the RAM
    # in one go, only to then raise an exception in the middle of the parsing, in
    # which case ~100 MB would have gone to waste.
    #
    # Reading files simultaneously, as we're doing, is the fastest and cheapest way,
    # but it also makes code a bit harder to read.
    ################################################################################
    namelist = _MemberNameList(iter(file.namelist()))

    # Argh, too many files...
    # https://stackoverflow.com/questions/4617034/how-can-i-open-multiple-files-using-with-open-in-python
    with contextlib.ExitStack() as stack:
        
        def open_file_on_stack(filename: str):
            # Files must be wrapped by `TextIOWrapper`, because `ZipFile.open()` opens files as streams of bytes.
            # https://stackoverflow.com/questions/15282651/how-do-i-read-text-files-within-a-zip-file
            return stack.enter_context(io.TextIOWrapper(file.open(filename), encoding='ISO-8859-1'))
        
        def make_readers(filenames: typing.Mapping[StatementType, str]) -> typing.Dict[StatementType, StatementReader]:
            return {
                StatementType.BPA:    BPxReader   (open_file_on_stack(filenames[StatementType.BPA])),
                StatementType.BPP:    BPxReader   (open_file_on_stack(filenames[StatementType.BPP])),
                StatementType.DRE:    DRxDVAReader(open_file_on_stack(filenames[StatementType.DRE])),
                StatementType.DRA:    DRxDVAReader(open_file_on_stack(filenames[StatementType.DRA])),
                StatementType.DFC_MD: DFCReader   (open_file_on_stack(filenames[StatementType.DFC_MD])),
                StatementType.DFC_MI: DFCReader   (open_file_on_stack(filenames[StatementType.DFC_MI])),
                StatementType.DMPL:   DMPLReader  (open_file_on_stack(filenames[StatementType.DMPL])),
                StatementType.DVA:    DRxDVAReader(open_file_on_stack(filenames[StatementType.DVA]))
            }

        head_reader = RegularDocumentHeadReader(open_file_on_stack(namelist.head_filename))

        if flag & BalanceFlag.INDIVIDUAL:
            ind_readers = make_readers(namelist.ind_filenames)
        else:
            ind_readers = {}

        if flag & BalanceFlag.CONSOLIDATED:
            con_readers = make_readers(namelist.con_filenames)
        else:
            con_readers = {}

        while True:
            try:
                head = head_reader.read()
            except StopIteration:
                break

            head_batch_id = _row_batch_id(head.cnpj, head.reference_date, head.version)

            # print(head.company_name, 'version:', head.version)

            def read_statements_mapped_by_type(readers):
                statements_by_type = collections.defaultdict(dict)

                for stmt_type, stmt_reader in readers.items():
                    try:
                        statements = stmt_reader.read(head_batch_id)
                    except (UnexpectedBatch, StopIteration):
                        continue

                    if stmt_type in (StatementType.DFC_MD, StatementType.DFC_MI):
                        stmt_type = StatementType.DFC

                    statements_by_type[stmt_type] = statements
                
                return statements_by_type

            ind_statements = read_statements_mapped_by_type(ind_readers)
            con_statements = read_statements_mapped_by_type(con_readers)

            try:
                if len(ind_statements) > 0:
                    # If at least one statement was read, all others must have been too.
                    individual = GroupedStatementCollection(datatypes.BalanceType.INDIVIDUAL, ind_statements)
                else:
                    # No statement was read. That means we have processed either:
                    # 1) An old version document that has no statements; or
                    # 2) A document that has individual statements only.
                    individual = None

                if len(con_statements) > 0:
                    consolidated = GroupedStatementCollection(datatypes.BalanceType.CONSOLIDATED, con_statements)
                else:
                    consolidated = None

            except KeyError as exc:
                # TODO: Throwing exceptions stops yielding further documents.
                #       Maybe store all exceptions and throw them in one go later?
                print(
                    f"failed to read {head.type.name} statements from document #{head.id} "
                    f"('{head.company_name}' version {head.version}): {exc}"
                )

                continue

            yield DFPITR(
                cnpj           = head.cnpj,
                reference_date = head.reference_date,
                version        = head.version,
                company_name   = head.company_name,
                cvm_code       = head.cvm_code,
                type           = head.type,
                id             = head.id,
                receipt_date   = head.receipt_date,
                url            = head.url,
                individual     = individual,
                consolidated   = consolidated
            )

def reader(file: typing.Union[zipfile.ZipFile, typing.IO, os.PathLike, str],
           flag: BalanceFlag = BalanceFlag.CONSOLIDATED|BalanceFlag.INDIVIDUAL
) -> typing.Generator[DFPITR, None, None]:

    if not isinstance(file, zipfile.ZipFile):
        file = zipfile.ZipFile(file)

    return _zip_reader(file, flag)