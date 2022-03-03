import enum
import zipfile
import os
import io
import contextlib
from typing                    import Union, IO, Optional, Iterable, Dict
from cvm.datatypes.statement   import StatementType
from cvm.parsing.dfp.document  import Document, DocumentReader
from cvm.parsing.dfp.statement import BPStatementReader, DStatementReader, DFCStatementReader, DMPLStatementReader, StatementCollection
from cvm.parsing.exceptions    import BadDocument

class BalanceFlag(enum.IntFlag):
    NONE         = 0
    CONSOLIDATED = 1
    INDIVIDUAL   = 2

class _MemberNameList:
    main_filename: str
    con_filenames: Dict[StatementType, str]
    ind_filenames: Dict[StatementType, str]

    def __init__(self, namelist: Iterable[str]):
        self.main_filename = ''
        self.con_filenames = {}
        self.ind_filenames = {}

        suffix_length = len('_XXXX.csv')

        for name in namelist:
            try:
                left_name = name[:-suffix_length]
            except IndexError:
                raise zipfile.BadZipFile(f"unexpected name for member file '{name}'")

            if   left_name == 'dfp_cia_aberta':            self.main_filename                       = name
            elif left_name == 'dfp_cia_aberta_BPA_con':    self.con_filenames[StatementType.BPA]    = name
            elif left_name == 'dfp_cia_aberta_BPA_ind':    self.ind_filenames[StatementType.BPA]    = name
            elif left_name == 'dfp_cia_aberta_BPP_con':    self.con_filenames[StatementType.BPP]    = name
            elif left_name == 'dfp_cia_aberta_BPP_ind':    self.ind_filenames[StatementType.BPP]    = name
            elif left_name == 'dfp_cia_aberta_DFC_MD_con': self.con_filenames[StatementType.DFC_MD] = name
            elif left_name == 'dfp_cia_aberta_DFC_MD_ind': self.ind_filenames[StatementType.DFC_MD] = name
            elif left_name == 'dfp_cia_aberta_DFC_MI_con': self.con_filenames[StatementType.DFC_MI] = name
            elif left_name == 'dfp_cia_aberta_DFC_MI_ind': self.ind_filenames[StatementType.DFC_MI] = name
            elif left_name == 'dfp_cia_aberta_DMPL_con':   self.con_filenames[StatementType.DMPL]   = name
            elif left_name == 'dfp_cia_aberta_DMPL_ind':   self.ind_filenames[StatementType.DMPL]   = name
            elif left_name == 'dfp_cia_aberta_DRA_con':    self.con_filenames[StatementType.DRA]    = name
            elif left_name == 'dfp_cia_aberta_DRA_ind':    self.ind_filenames[StatementType.DRA]    = name
            elif left_name == 'dfp_cia_aberta_DRE_con':    self.con_filenames[StatementType.DRE]    = name
            elif left_name == 'dfp_cia_aberta_DRE_ind':    self.ind_filenames[StatementType.DRE]    = name
            elif left_name == 'dfp_cia_aberta_DVA_con':    self.con_filenames[StatementType.DVA]    = name
            elif left_name == 'dfp_cia_aberta_DVA_ind':    self.ind_filenames[StatementType.DVA]    = name
            else:
                raise zipfile.BadZipFile(f"unknown member file '{name}'")

def _make_generator(file, mode, flag: BalanceFlag) -> Document:
    """Creates a generator that reads one document at a time."""

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
    # The first CSV in the above list is what I call the "main file." All other CSV
    # files are "statement files." Data in statement files are structured according
    # to the rows in the main file.
    # 
    # Every row in the main file results in a corresponding `Document` object, which
    # will be yielded by this generator along with any statements the document has.
    #
    # All these files are read simultaneously. Why not open all CSV files, extract
    # their data, and *then* process everything? Well, every extracted ZIP file is
    # ~200 MB. It doesn't sound like a good idea to me to store 200 MB on the RAM
    # in one go, only to then raise an exception in the middle of the parsing, in
    # which case ~100 MB would have gone to waste.
    #
    # Reading files simultaneously, as we're doing, is the fastest and cheapest way,
    # but it also makes code harder to read.
    ################################################################################
    with zipfile.ZipFile(file, mode=mode) as zfile:
        encoding = 'ISO-8859-1'
        namelist = _MemberNameList(iter(zfile.namelist()))

        # Argh, too many files...
        # https://stackoverflow.com/questions/4617034/how-can-i-open-multiple-files-using-with-open-in-python
        with contextlib.ExitStack() as stack:

            # Files must be wrapped by `TextIOWrapper`, because `ZipFile.open()` opens files as streams of bytes.
            # https://stackoverflow.com/questions/15282651/how-do-i-read-text-files-within-a-zip-file
            doc_filename = namelist.main_filename
            doc_file     = stack.enter_context(io.TextIOWrapper(zfile.open(doc_filename), encoding=encoding))
            doc_reader   = DocumentReader(doc_file)
            con_readers  = {}
            ind_readers  = {}

            def open_statement_file(filename_dict, stmt_type: StatementType):
                stmt_filename = filename_dict[stmt_type]
                stmt_file     = stack.enter_context(io.TextIOWrapper(zfile.open(stmt_filename), encoding=encoding))
                return stmt_file

            def create_statement_reader(reader_dict, filename_dict, stmt_type, ReaderType):
                stmt_file              = open_statement_file(filename_dict, stmt_type)
                reader_dict[stmt_type] = ReaderType(stmt_file)

            if flag & BalanceFlag.CONSOLIDATED:
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.BPA,    BPStatementReader)
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.BPP,    BPStatementReader)
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.DRE,    DStatementReader)
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.DRA,    DStatementReader)
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.DFC_MD, DFCStatementReader)
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.DFC_MI, DFCStatementReader)
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.DMPL,   DMPLStatementReader)
                create_statement_reader(con_readers, namelist.con_filenames, StatementType.DVA,    DStatementReader)

            if flag & BalanceFlag.INDIVIDUAL:
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.BPA,    BPStatementReader)
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.BPP,    BPStatementReader)
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.DRE,    DStatementReader)
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.DRA,    DStatementReader)
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.DFC_MD, DFCStatementReader)
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.DFC_MI, DFCStatementReader)
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.DMPL,   DMPLStatementReader)
                create_statement_reader(ind_readers, namelist.ind_filenames, StatementType.DVA,    DStatementReader)

            ################################################################################
            # Cached statements are used in case we have read a statement from a statement
            # file (BPA, BPP, etc.), but haven't read a matching line from the reference
            # file yet. For example, consider the first three lines from the main file of
            # DFP 2020 ("dfp_cia_aberta_2020.csv"):
            #
            # CNPJ_CIA	           DT_REFER     VERSAO   DENOM_CIA                  CD_CVM   CATEG_DOC   ID_DOC   DT_RECEB     ...
            # 00.000.000/0001-91   2020-12-31   1        BCO BRASIL S.A.            1023     DFP         100120   2021-02-11   ...
            # 00.000.000/0001-91   2020-12-31   2        BCO BRASIL S.A.            1023     DFP         102382   2021-03-29   ...
            # 00.000.208/0001-00   2020-12-31   1        BRB BCO DE BRASILIA S.A.   14206    DFP         100147   2021-02-12   ...
            #
            # You can see that the first two lines contain information about two documents
            # of the same company ("BCO BRASIL S.A.").
            #
            # However, statement files typically contain balances of the last version only.
            # Here's the first two lines of the consolidated BPA file of that same year
            # ("dfp_cia_aberta_BPA_con_2020.csv"):
            #
            # CNPJ_CIA             DT_REFER     VERSAO   DENOM_CIA         ...
            # 00.000.000/0001-91   2020-12-31   2        BCO BRASIL S.A.   ...
            # 00.000.000/0001-91   2020-12-31   2        BCO BRASIL S.A.   ...
            #
            # As you see, there are no BPA balances for version 1 of "BCO BRASIL S.A." Why?
            # Because old document versions don't matter, I guess. Anyway, most documents
            # will have statements only for their last version, with very few of them having
            # more than one. In the case of "BCO BRASIL S.A.", we only have statements for
            # version 2 of its document on year 2020.
            ################################################################################
            cached_con_statements = {}
            cached_ind_statements = {}

            for doc in doc_reader:
                doc_group_id = doc.group_id()

                def create_statement_collection(readers, cached_statements) -> Optional[StatementCollection]:
                    statements = {}

                    for stmt_type, reader in readers.items():
                        # Pop a statement of the given statement type from the cache, if any.
                        statement = cached_statements.pop(stmt_type, None)

                        if statement is None:
                            # No cached statement found, so read a new one from the file.
                            # TODO: catch StopIteration
                            statement = next(reader)

                        if statement.group_id() == doc_group_id:
                            # We got a statement of the same group as the document.
                            # Store it into `statements` and proceed to read other statements.
                            statements[stmt_type] = statement
                            continue
                        else:
                            # We got a statement, but it's part of another document,
                            # so put it (back) into the cache.
                            cached_statements[stmt_type] = statement

                            if stmt_type not in (StatementType.DFC_MD, StatementType.DFC_MI):
                                break
                    
                    if len(statements) > 0:
                        # At least one statement was read, so pass the read statements on to
                        # `StatementCollection`, which shall also verify we got 'em all.
                        try:
                            return StatementCollection(statements)
                        except BadDocument as exc:
                            raise BadDocument(f'failed to read statements of document {doc}: {exc}') from None
                    else:
                        # No statement was read. That means we have processed either:
                        # 1) An old version document that has no statements; or
                        # 2) A document that has statements for one balance type only (consolidated or individual).
                        return None

                doc.consolidated = create_statement_collection(con_readers, cached_con_statements)
                doc.individual   = create_statement_collection(ind_readers, cached_ind_statements)

                yield doc

class ZipReader:
    """Reads DFP `Documents` from a ZIP file.
    
    >>> dfp_reader = ZipReader('path/to/dfp.zip')
    >>> for doc in dfp_reader:
    ...     print(doc)
    """

    __slots__ = ['_filepath', '_flag', '_reader']

    def __init__(self, file: Union[str, IO], flag: BalanceFlag = BalanceFlag.CONSOLIDATED|BalanceFlag.INDIVIDUAL):
        if isinstance(file, (str, os.PathLike)):
            self._reader   = _make_generator(file, 'r', flag)
            self._flag     = flag
            self._filepath = file
        else:
            self._reader   = _make_generator(file, ..., flag)
            self._flag     = flag
            self._filepath = file.name

    def __iter__(self):
        return self

    def __next__(self) -> Document:
        doc = next(self._reader)
        return doc

    def __repr__(self) -> str:
        return f"<ZipReader name='{self._filepath}' flag={self._flag}>"

class ZipWriter:
    def __init__(self, file: Union[str, IO], flag: BalanceFlag = BalanceFlag.CONSOLIDATED|BalanceFlag.INDIVIDUAL):
        if isinstance(file, (str, os.PathLike)):
            mode = 'w'
        else:
            mode = ...

        zfile = zipfile.ZipFile(file, mode=mode)

    def write(self, doc: Document):
        ...