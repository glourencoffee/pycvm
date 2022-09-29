from __future__ import annotations
import collections
import contextlib
import datetime
import decimal
import enum
import functools
import io
import os
import typing
import zipfile
import zlib
from cvm import datatypes
from cvm.csvio.batch import CSVBatch
from cvm.csvio.document      import RegularDocumentHeadReader, RegularDocumentBodyReader, UnexpectedBatch
from cvm.csvio.row           import CSVRow
from cvm.datatypes.currency  import Currency, CurrencySize
from cvm.datatypes.tax_id    import CNPJ
from cvm.datatypes.statement import GroupedStatementCollection, StatementType, Statement, DFCMethod, FiscalYearOrder, BPx, DRxDVA, DFC, DMPL
from cvm.datatypes.document  import DFPITR
from cvm.exceptions          import ZipMemberError, NotImplementedException, InvalidValueError, BadDocument
from cvm.utils               import date_from_string

__all__ = [
    'dfpitr_reader',
    'DFPITRFile'
]

class _StatementFileNames:
    bpa: str
    bpp: str
    dfc_md: str
    dfc_mi: str
    dmpl: str
    dra: str
    dre: str
    dva: str

class _MemberNameList:
    head: str
    con: _StatementFileNames
    ind: _StatementFileNames

    def __init__(self, namelist: typing.Iterable[str]):
        self.head = ''
        self.con  = _StatementFileNames()
        self.ind  = _StatementFileNames()

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

            if   middle_name == '':            self.head       = name
            elif middle_name == '_BPA_con':    self.con.bpa    = name
            elif middle_name == '_BPA_ind':    self.ind.bpa    = name
            elif middle_name == '_BPP_con':    self.con.bpp    = name
            elif middle_name == '_BPP_ind':    self.ind.bpp    = name
            elif middle_name == '_DFC_MD_con': self.con.dfc_md = name
            elif middle_name == '_DFC_MD_ind': self.ind.dfc_md = name
            elif middle_name == '_DFC_MI_con': self.con.dfc_mi = name
            elif middle_name == '_DFC_MI_ind': self.ind.dfc_mi = name
            elif middle_name == '_DMPL_con':   self.con.dmpl   = name
            elif middle_name == '_DMPL_ind':   self.ind.dmpl   = name
            elif middle_name == '_DRA_con':    self.con.dra    = name
            elif middle_name == '_DRA_ind':    self.ind.dra    = name
            elif middle_name == '_DRE_con':    self.con.dre    = name
            elif middle_name == '_DRE_ind':    self.ind.dre    = name
            elif middle_name == '_DVA_con':    self.con.dva    = name
            elif middle_name == '_DVA_ind':    self.ind.dva    = name
            else:
                raise ZipMemberError(name)

def _make_row_batch_id(cnpj: CNPJ, reference_date: datetime.date, version: int) -> int:
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
    @staticmethod
    @functools.lru_cache
    def fiscal_year_orders() -> typing.Dict[str, FiscalYearOrder]:
        return {
            'ÚLTIMO':    FiscalYearOrder.LAST,
            'PENÚLTIMO': FiscalYearOrder.SECOND_TO_LAST,
        }

    @staticmethod
    @functools.lru_cache
    def currencies() -> typing.Dict[str, Currency]:
        return {
            'REAL': Currency.BRL
        }

    @staticmethod
    @functools.lru_cache
    def currency_sizes() -> typing.Dict[str, CurrencySize]:
        return {
            'UNIDADE': CurrencySize.UNIT,
            'MIL':     CurrencySize.THOUSAND,
        }

    @classmethod
    def make_fiscal_year_order(cls, value: str) -> FiscalYearOrder:
        return cls.fiscal_year_orders()[value]

    @classmethod
    def make_currency(cls, value: str) -> Currency:
        return cls.currencies()[value]

    @classmethod
    def make_currency_size(cls, value: str) -> CurrencySize:
        return cls.currency_sizes()[value]

    def batch_id(self, row: CSVRow) -> int:
        cnpj           = row.required('CNPJ_CIA', CNPJ.from_zfilled_with_separators)
        reference_date = row.required('DT_REFER', date_from_string)
        version        = row.required('VERSAO',   int)

        return _make_row_batch_id(cnpj, reference_date, version)

    def read(self, expected_batch_id: int):
        batch = self.read_expected_batch(expected_batch_id)
        stmts = self.read_statements(batch)

        return stmts

    def read_account(self, row: CSVRow) -> datatypes.Account:
        return datatypes.Account(
            code      = row.required('CD_CONTA',      str),
            name      = row.optional('DS_CONTA',      str),
            quantity  = row.required('VL_CONTA',      decimal.Decimal),
            is_fixed  = row.required('ST_CONTA_FIXA', str) == 'S'
        )

    def read_accounts(self, rows: typing.List[CSVRow]) -> typing.List[datatypes.Account]:
        return [self.read_account(row) for row in rows]

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
            fiscal_year_order = first_row.required('ORDEM_EXERC',  self.make_fiscal_year_order),
            currency          = first_row.required('MOEDA',        self.make_currency),
            currency_size     = first_row.required('ESCALA_MOEDA', self.make_currency_size),
            period_end_date   = first_row.required('DT_FIM_EXERC', date_from_string),
            accounts          = self.read_accounts(rows)
        )

class DRxDVAReader(StatementReader):
    def group_key_fields(self) -> typing.Sequence[str]:
        return ('ORDEM_EXERC', 'DT_INI_EXERC', 'DT_FIM_EXERC')

    def create_statement(self, rows: typing.List[CSVRow]) -> DRxDVA:
        first_row = rows[0]

        return DRxDVA(
            fiscal_year_order = first_row.required('ORDEM_EXERC',  self.make_fiscal_year_order),
            currency          = first_row.required('MOEDA',        self.make_currency),
            currency_size     = first_row.required('ESCALA_MOEDA', self.make_currency_size),
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

        if   dfc_method_name == 'Método Direto':   dfc_method = DFCMethod.DIRECT
        elif dfc_method_name == 'Método Indireto': dfc_method = DFCMethod.INDIRECT
        else:
            raise InvalidValueError(f"unknown DFC method '{dfc_method_name}' at field 'GRUPO_DFP'")

        return DFC(
            fiscal_year_order = first_row.required('ORDEM_EXERC',  self.make_fiscal_year_order),
            currency          = first_row.required('MOEDA',        self.make_currency),
            currency_size     = first_row.required('ESCALA_MOEDA', self.make_currency_size),
            method            = dfc_method,
            period_start_date = first_row.required('DT_INI_EXERC', date_from_string),
            period_end_date   = first_row.required('DT_FIM_EXERC', date_from_string),
            accounts          = self.read_accounts(rows)
        )

class DMPLReader(StatementReader):
    # I know, I know, this is ugly as fuck, but uglier than this
    # is extracting incorrect data due to CVM's mis-generation of
    # DFP/ITR files. See issue #9.
    should_fix_quantities = False

    def group_key_fields(self) -> typing.Sequence[str]:
        return ('ORDEM_EXERC', 'DT_INI_EXERC', 'DT_FIM_EXERC')

    def create_dmpl_account(self, code: str, name: str, is_fixed: bool, quantities: typing.Dict[str, int]) -> datatypes.DMPLAccount:
        # TODO
        # The below reading of attributes from `quantities`
        # raises `KeyError` if a required column is missing.
        # Should we re-raise it as another exception defined
        # by this library?
        return datatypes.DMPLAccount(
            code                                = code,
            name                                = name,
            is_fixed                            = is_fixed,
            share_capital                       = quantities['Capital Social Integralizado'],
            capital_reserve_and_treasury_shares = quantities['Reservas de Capital, Opções Outorgadas e Ações em Tesouraria'],
            profit_reserves                     = quantities['Reservas de Lucro'],
            unappropriated_retained_earnings    = quantities['Lucros ou Prejuízos Acumulados'],
            other_comprehensive_income          = quantities['Outros Resultados Abrangentes'],
            controlling_interest                = quantities['Patrimônio Líquido'],
            non_controlling_interest            = quantities.get('Participação dos Não Controladores', None),
            consolidated_equity                 = quantities.get('Patrimônio Líquido Consolidado', None)
        )

    @staticmethod
    def fix_quantities(quantities: typing.Dict[str, int]) -> typing.Dict[str, int]:
        # Bugfix for issue #9.

        fixed_quantities = {}
        prev_column = ''

        for i, (column, quantity) in enumerate(quantities.items()):
            if i < 3:
                # Capital Social Integralizado
                # Reservas de Capital, Opções Outorgadas e Ações em Tesouraria
                # Reservas de Lucro
                fixed_quantities[column] = quantity

            elif i == 3:
                fixed_quantities['Ajustes de Avaliação Patrimonial'] = quantity

            else:
                fixed_quantities[prev_column] = quantity

            prev_column = column

        return fixed_quantities

    def create_statement(self, rows: typing.List[CSVRow]) -> DMPL:
        first_row = rows[0]

        last_account  = None
        quantities    = {}
        dmpl_accounts = []

        for row in rows:
            column  = row.required('COLUNA_DF', str, allow_empty_string=True)
            account = self.read_account(row)
            
            if last_account is not None and account.name != last_account.name:
                if self.should_fix_quantities:
                    quantities = self.fix_quantities(quantities)

                dmpl_account = self.create_dmpl_account(
                    code       = last_account.code,
                    name       = last_account.name,
                    is_fixed   = last_account.is_fixed,
                    quantities = quantities
                )

                dmpl_accounts.append(dmpl_account)
                quantities.clear()

            quantities[column] = account.quantity
            last_account = account

        if last_account is not None:
            if self.should_fix_quantities:
                quantities = self.fix_quantities(quantities)

            dmpl_account = self.create_dmpl_account(
                code       = last_account.code,
                name       = last_account.name,
                is_fixed   = last_account.is_fixed,
                quantities = quantities
            )

            dmpl_accounts.append(dmpl_account)

        return DMPL(
            fiscal_year_order = first_row.required('ORDEM_EXERC',  self.make_fiscal_year_order),
            currency          = first_row.required('MOEDA',        self.make_currency),
            currency_size     = first_row.required('ESCALA_MOEDA', self.make_currency_size),
            period_start_date = first_row.required('DT_INI_EXERC', date_from_string),
            period_end_date   = first_row.required('DT_FIM_EXERC', date_from_string),
            accounts          = dmpl_accounts
        )

def _open_zip_member_on_stack(stack: contextlib.ExitStack, archive: zipfile.ZipFile, filename: str):
    member = archive.open(filename, mode='r')
    stream = io.TextIOWrapper(member, encoding='iso-8859-1')

    return stack.enter_context(stream)

def _make_readers(stack: contextlib.ExitStack,
                  archive: zipfile.ZipFile,
                  filenames: _StatementFileNames
) -> typing.List[typing.Tuple[StatementType, StatementReader]]:

    return [
        (StatementType.BPA,  BPxReader   (_open_zip_member_on_stack(stack, archive, filenames.bpa))),
        (StatementType.BPP,  BPxReader   (_open_zip_member_on_stack(stack, archive, filenames.bpp))),
        (StatementType.DRE,  DRxDVAReader(_open_zip_member_on_stack(stack, archive, filenames.dre))),
        (StatementType.DRA,  DRxDVAReader(_open_zip_member_on_stack(stack, archive, filenames.dra))),
        (StatementType.DFC,  DFCReader   (_open_zip_member_on_stack(stack, archive, filenames.dfc_md))),
        (StatementType.DFC,  DFCReader   (_open_zip_member_on_stack(stack, archive, filenames.dfc_mi))),
        (StatementType.DMPL, DMPLReader  (_open_zip_member_on_stack(stack, archive, filenames.dmpl))),
        (StatementType.DVA,  DRxDVAReader(_open_zip_member_on_stack(stack, archive, filenames.dva)))
    ]

def _read_all_statements(batch_id: int, readers: typing.List[typing.Tuple[StatementType, StatementReader]]) -> typing.Dict[StatementType, Statement]:
    all_statements = collections.defaultdict(dict)

    for stmt_type, stmt_reader in readers:
        try:
            statements = stmt_reader.read(batch_id)
        except (UnexpectedBatch, StopIteration):
            continue

        all_statements[stmt_type] = statements
    
    return all_statements

def dfpitr_reader(archive: zipfile.ZipFile, consolidated: bool, individual: bool) -> typing.Generator[DFPITR, None, None]:
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
    namelist = _MemberNameList(iter(archive.namelist()))

    # Argh, too many files...
    # https://stackoverflow.com/questions/4617034/how-can-i-open-multiple-files-using-with-open-in-python
    with contextlib.ExitStack() as stack:
        head_reader = RegularDocumentHeadReader(_open_zip_member_on_stack(stack, archive, namelist.head))

        if individual:
            ind_readers = _make_readers(stack, archive, namelist.ind)
        else:
            ind_readers = {}

        if consolidated:
            con_readers = _make_readers(stack, archive, namelist.con)
        else:
            con_readers = {}

        while True:
            try:
                head = head_reader.read()
            except StopIteration:
                break

            head_batch_id = _make_row_batch_id(head.cnpj, head.reference_date, head.version)

            # See issue #9.
            DMPLReader.should_fix_quantities = (head.reference_date.year >= 2020)

            ind_statements = _read_all_statements(head_batch_id, ind_readers)
            con_statements = _read_all_statements(head_batch_id, con_readers)

            try:
                if len(ind_statements) > 0:
                    # If at least one statement was read, all others must have been too.
                    if head.type == datatypes.DocumentType.DFP:
                        individual = GroupedStatementCollection.from_dfp_statements(datatypes.BalanceType.INDIVIDUAL, ind_statements)
                    else:
                        individual = GroupedStatementCollection.from_itr_statements(datatypes.BalanceType.INDIVIDUAL, ind_statements)
                else:
                    # No statement was read. That means we have processed either:
                    # 1) An old version document that has no statements; or
                    # 2) A document that has only consolidated statements.
                    individual = None

            except KeyError as exc:
                print('Skipping individual balances of ', head.type.name, ' document #', head.id, " ('", head.company_name, "' version ", head.version, '): ', exc, sep='')
                individual = None

            try:
                if len(con_statements) > 0:
                    if head.type == datatypes.DocumentType.DFP:
                        consolidated = GroupedStatementCollection.from_dfp_statements(datatypes.BalanceType.CONSOLIDATED, con_statements)
                    else:
                        consolidated = GroupedStatementCollection.from_itr_statements(datatypes.BalanceType.CONSOLIDATED, con_statements)
                else:
                    # No statement was read. That means we have processed either:
                    # 1) An old version document that has no statements; or
                    # 2) A document that has only individual statements.
                    consolidated = None

            except KeyError as exc:
                print('Skipping consolidated balances of ', head.type.name, ' document #', head.id, " ('", head.company_name, "' version ", head.version, '): ', exc, sep='')
                consolidated = None

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

class DFPITRFile(zipfile.ZipFile):
    """Class for reading `DFPITR` objects from a DFP/ITR file."""

    def __init__(self,
                 file: typing.Union[os.PathLike, typing.IO[bytes]],
                 consolidated: bool = True,
                 individual: bool = True
    ) -> None:
        """Opens the DFP/ITR file in read mode."""

        super().__init__(file, mode='r')

        self._reader = dfpitr_reader(archive=self, consolidated=consolidated, individual=individual)

    def __iter__(self) -> DFPITRFile:
        return self

    def __next__(self) -> DFPITR:
        return next(self._reader)