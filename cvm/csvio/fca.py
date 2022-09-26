from __future__ import annotations
import contextlib
import io
import os
import typing
import zipfile
from cvm                import datatypes, exceptions, utils
from cvm.csvio.batch    import CSVBatch
from cvm.csvio.document import RegularDocumentHeadReader, RegularDocumentBodyReader, UnexpectedBatch
from cvm.csvio.row      import CSVRow

__all__ = [
    'fca_reader',
    'FCAFile'
]

class _MemberNameList:
    head_filename: str
    auditor_filename: str
    dissemination_channel_filename: str
    shareholder_department_filename: str
    investor_relations_department_filename: str
    address_filename: str
    bookkeeper_filename: str
    general_filename: str
    foreign_country_filename: str
    securities_filename: str

    def __init__(self, namelist: typing.Iterable[str]):
        self.head_filename                          = ''
        self.auditor_filename                       = ''
        self.dissemination_channel_filename         = ''
        self.shareholder_department_filename        = ''
        self.investor_relations_department_filename = ''
        self.address_filename                       = ''
        self.bookkeeper_filename                    = ''
        self.general_filename                       = ''
        self.foreign_country_filename               = ''
        self.securities_filename                    = ''

        suffix_length = len('_YYYY.csv')

        for name in namelist:
            try:
                left_name = name[:-suffix_length]
            except IndexError:
                raise zipfile.BadZipFile(f"unexpected name for member file '{name}'")

            if   left_name == 'fca_cia_aberta':                             self.head_filename                          = name
            elif left_name == 'fca_cia_aberta_auditor':                     self.auditor_filename                       = name
            elif left_name == 'fca_cia_aberta_canal_divulgacao':            self.dissemination_channel_filename         = name
            elif left_name == 'fca_cia_aberta_departamento_acionistas':     self.shareholder_department_filename        = name
            elif left_name == 'fca_cia_aberta_dri':                         self.investor_relations_department_filename = name
            elif left_name == 'fca_cia_aberta_endereco':                    self.address_filename                       = name
            elif left_name == 'fca_cia_aberta_escriturador':                self.bookkeeper_filename                    = name
            elif left_name == 'fca_cia_aberta_geral':                       self.general_filename                       = name
            elif left_name == 'fca_cia_aberta_pais_estrangeiro_negociacao': self.foreign_country_filename               = name
            elif left_name == 'fca_cia_aberta_valor_mobiliario':            self.securities_filename                    = name
            else:
                raise zipfile.BadZipFile(f"unknown member file '{name}'")

class CommonReader(RegularDocumentBodyReader):
    @classmethod
    def read_country(cls, row: CSVRow, fieldname: str) -> typing.Optional[datatypes.Country]:
        country_name = row[fieldname]

        if country_name in ('', 'N/A', 'Não aplicável'):
            return None

        try:
            return datatypes.Country(country_name)
        except ValueError:
            #===========================================================
            # Below is what happens when you don't enforce valid country
            # names at GUI level, but instead let user type out country
            # names and accept them as is. Argh.
            #===========================================================

            if country_name in ('Brasi', 'BR', 'São Paulo'):
                return datatypes.Country.BR
            
            if country_name == 'Espanhã':
                return datatypes.Country.ES
            
            if country_name in ('Reino Unido', 'Inglaterra'):
                return datatypes.Country.GB

            if country_name in ('Nova Iorque', 'EUA', 'Estados Unidos da América'):
                return datatypes.Country.US

            if country_name == 'Luxemburgo.':
                return datatypes.Country.LU

            if country_name == 'Canadá Toronto Stock Exchange Venture (TSX-V)':
                return datatypes.Country.CA

            if country_name == 'Suiça':
                return datatypes.Country.CH

            print('[', cls.__name__, "] Unknown country name '", country_name, "' at field '", fieldname, "'", sep='')
            return None

    @classmethod
    def read_address(cls, row: CSVRow) -> datatypes.Address:
        return datatypes.Address(
            street      = row.required('Logradouro',   str, allow_empty_string=True),
            complement  = row.optional('Complemento',  str, allow_empty_string=True),
            district    = row.required('Bairro',       str, allow_empty_string=True),
            city        = row.required('Cidade',       str, allow_empty_string=True),
            state       = row.required('Sigla_UF',     str, allow_empty_string=True),
            country     = cls.read_country(row, 'Pais'),
            postal_code = row.required('CEP',          int)
        )

    @classmethod
    def read_phone(cls, row: CSVRow) -> datatypes.Phone:
        # TODO
        # Some phones have misassigned area codes in some FCA files.
        # For example, the correct row would be:
        #
        # DDI_Telefone | DDD_Telefone | Telefone
        # -------------|--------------|---------
        #     55       |      11      | 12345678
        #
        # However, some files have rows like this:
        #
        # DDI_Telefone | DDD_Telefone | Telefone
        # -------------|--------------|---------
        #              |    5511      | 12345678
        #
        # There is no area code 5511 in Brazil, so clearly,
        # 55 means the country code. Maybe the person who
        # sent the company data to CVM inputted it wrongly,
        # or maybe CVM generated the file wrongly.
        # 
        # Also, it is possible that "DDD_Telefone" is not
        # specified because it is given in "Telefone":
        #
        # DDI_Telefone | DDD_Telefone | Telefone
        # -------------|--------------|-----------
        #              |              | 1112345678
        #
        # I know, it's annoying that CVM files lack a proper
        # structure, but anyway, should this library fix cases
        # like this or leave it as is?

        return datatypes.Phone(
            country_code = row.optional('DDI_Telefone', int, allow_empty_string=False),
            area_code    = row.required('DDD_Telefone', int),
            number       = row.required('Telefone',     int)
        )

    @classmethod
    def read_fax(cls, row: CSVRow) -> datatypes.Phone:
        return datatypes.Phone(
            country_code = row.optional('DDI_Fax', int, allow_empty_string=False),
            area_code    = row.required('DDD_Fax', int),
            number       = row.required('Fax',     int)
        )

    @classmethod
    def read_contact(cls, row: CSVRow) -> datatypes.Contact:
        try:
            phone = cls.read_phone(row)
        except exceptions.BadDocument:
            phone = None

        try:
            fax = cls.read_fax(row)
        except exceptions.BadDocument:
            fax = None

        return datatypes.Contact(
            phone = phone,
            fax   = fax,
            email = row.optional('Email', str)
        )

    @classmethod
    def read_many(cls, batch: CSVBatch, read_function: typing.Callable[[CSVRow], typing.Any]) -> typing.List[typing.Any]:
        items = []

        for line, row in enumerate(batch, start=1):
            try:
                item = read_function(row)
            except exceptions.BadDocument as exc:
                print('[', cls.__name__, '] Skipping line ', line, ' in batch ', batch.id, sep='', end='')
                print(':', exc)
            else:
                items.append(item)

        return items

    def batch_id(self, row: CSVRow) -> int:
        return row.required('ID_Documento', int)

class AddressReader(CommonReader):
    """'fca_cia_aberta_endereco_YYYY.csv'"""

    def read(self, document_id: int) -> typing.List[datatypes.Address]:
        batch     = self.read_expected_batch(document_id)
        addresses = self.read_many(batch, self.read_address)

        return addresses

class TradingAdmissionReader(CommonReader):
    """'fca_cia_aberta_pais_estrangeiro_negociacao_YYYY.csv'"""

    @classmethod
    def read_trading_admission(cls, row: CSVRow) -> datatypes.TradingAdmission:
        return datatypes.TradingAdmission(
            foreign_country = cls.read_country(row, 'Pais'),
            admission_date  = row.required('Data_Admissao_Negociacao', utils.date_from_string)
        )

    def read(self, document_id: int) -> typing.List[datatypes.TradingAdmission]:
        batch              = self.read_expected_batch(document_id)
        trading_admissions = self.read_many(batch, self.read_trading_admission)

        return trading_admissions

class IssuerCompanyReader(CommonReader):
    """'fca_cia_aberta_geral_YYYY.csv'"""

    def read(self,
             document_id: int,
             trading_admissions: typing.Sequence[datatypes.TradingAdmission],
             addresses: typing.Sequence[datatypes.Address]
    ) -> datatypes.IssuerCompany:

        batch = self.read_expected_batch(document_id)
        row   = batch.rows[0]

        return datatypes.IssuerCompany(
            corporate_name                    = row.required('Nome_Empresarial',                  str),
            corporate_name_last_changed       = row.optional('Data_Nome_Empresarial',             utils.date_from_string),
            previous_corporate_name           = row.optional('Nome_Empresarial_Anterior',         str, allow_empty_string=False),
            establishment_date                = row.required('Data_Constituicao',                 utils.date_from_string),
            cnpj                              = row.required('CNPJ_Companhia',                    datatypes.CNPJ.from_zfilled_with_separators),
            cvm_code                          = row.required('Codigo_CVM',                        utils.lzstrip),
            cvm_registration_date             = row.required('Data_Registro_CVM',                 utils.date_from_string),
            cvm_registration_category         = row.required('Categoria_Registro_CVM',            datatypes.RegistrationCategory),
            cvm_registration_category_started = row.required('Data_Categoria_Registro_CVM',       utils.date_from_string),
            cvm_registration_status           = row.required('Situacao_Registro_CVM',             datatypes.RegistrationStatus),
            cvm_registration_status_started   = row.required('Data_Situacao_Registro_CVM',        utils.date_from_string),
            home_country                      = self.read_country(row, 'Pais_Origem'),
            securities_custody_country        = self.read_country(row, 'Pais_Custodia_Valores_Mobiliarios'),
            trading_admissions                = tuple(iter(trading_admissions)),
            industry                          = row.required('Setor_Atividade',                   datatypes.Industry),
            issuer_status                     = row.required('Situacao_Emissor',                  datatypes.IssuerStatus),
            issuer_status_started             = row.required('Data_Situacao_Emissor',             utils.date_from_string),
            controlling_interest              = row.required('Especie_Controle_Acionario',        datatypes.ControllingInterest),
            controlling_interest_last_changed = row.optional('Data_Especie_Controle_Acionario',   utils.date_from_string),
            fiscal_year_end_day               = row.required('Dia_Encerramento_Exercicio_Social', int),
            fiscal_year_end_month             = row.required('Mes_Encerramento_Exercicio_Social', int),
            fiscal_year_last_changed          = row.optional('Data_Alteracao_Exercicio_Social',   utils.date_from_string),
            webpage                           = row.optional('Pagina_Web',                        str),
            communication_channels            = (),
            addresses                         = tuple(iter(addresses)),
            contact                           = None # TODO
        )

class SecurityReader(CommonReader):
    """'fca_cia_aberta_valor_mobiliario_YYYY.csv'"""

    @classmethod
    def read_security(cls, row: CSVRow) -> datatypes.Security:
        return datatypes.Security(
            type                          = row.required('Valor_Mobiliario',              datatypes.SecurityType),
            market_type                   = row.required('Mercado',                       datatypes.MarketType),
            market_managing_entity_symbol = row.required('Sigla_Entidade_Administradora', str),
            market_managing_entity_name   = row.required('Entidade_Administradora',       str),
            preferred_share_type          = row.optional('Classe_Acao_Preferencial',      datatypes.PreferredShareType),
            bdr_unit_composition          = row.optional('Composicao_BDR_Unit',           str),
            trading_symbol                = row.optional('Codigo_Negociacao',             str),
            trading_started               = row.optional('Data_Inicio_Negociacao',        utils.date_from_string),
            trading_ended                 = row.optional('Data_Fim_Negociacao',           utils.date_from_string),
            market_segment                = row.optional('Segmento',                      datatypes.MarketSegment),
            listing_started               = row.optional('Data_Inicio_Listagem',          utils.date_from_string),
            listing_ended                 = row.optional('Data_Fim_Listagem',             utils.date_from_string)
        )

    def read(self, document_id: int) -> typing.List[datatypes.Security]:
        batch      = self.read_expected_batch(document_id)
        securities = self.read_many(batch, self.read_security)

        return securities

class AuditorReader(CommonReader):
    """'fca_cia_aberta_auditor_YYYY.csv'"""

    @classmethod
    def read_auditor(cls, row: CSVRow) -> datatypes.Auditor:
        tax_id_str = row.required('CPF_CNPJ_Auditor', str)

        try:
            tax_id = datatypes.CNPJ.from_zfilled_with_separators(tax_id_str)
        except datatypes.InvalidTaxID:
            try:
                tax_id = datatypes.CPF.from_zfilled_with_separators(tax_id_str)
            except datatypes.InvalidTaxID as exc:
                raise exc from None

        return datatypes.Auditor(
            name                                = row.required('Auditor',                                 str),
            tax_id                              = tax_id,
            cvm_code                            = row.required('Codigo_CVM_Auditor',                      utils.lzstrip),
            activity_started                    = row.required('Data_Inicio_Atuacao_Auditor',             utils.date_from_string),
            activity_ended                      = row.optional('Data_Fim_Atuacao_Auditor',                utils.date_from_string),
            technical_manager_name              = row.required('Responsavel_Tecnico',                     str),
            technical_manager_cpf               = row.required('CPF_Responsavel_Tecnico',                 datatypes.CPF.from_zfilled_with_separators),
            technical_manager_activity_started  = row.required('Data_Inicio_Atuacao_Responsavel_Tecnico', utils.date_from_string),
            technical_manager_activity_ended    = row.optional('Data_Fim_Atuacao_Responsavel_Tecnico',    utils.date_from_string),
        )

    def read(self, document_id: int) -> typing.List[datatypes.Auditor]:
        batch    = self.read_expected_batch(document_id)
        auditors = self.read_many(batch, self.read_auditor)

        return auditors

class BookkeepingAgentReader(CommonReader):
    """'fca_cia_aberta_escriturador_YYYY.csv'"""

    @classmethod
    def read_bookkeeping_agent(cls, row: CSVRow) -> datatypes.BookkeepingAgent:
        return datatypes.BookkeepingAgent(
            name             = row.required('Escriturador',      str),
            cnpj             = row.required('CNPJ_Escriturador', datatypes.CNPJ.from_zfilled_with_separators),
            address          = cls.read_address(row),
            contact          = cls.read_contact(row),
            activity_started = row.optional('Data_Inicio_Atuacao', utils.date_from_string),
            activity_ended   = row.optional('Data_Fim_Atuacao',    utils.date_from_string)
        )

    def read(self, document_id: int) -> typing.List[datatypes.BookkeepingAgent]:
        batch              = self.read_expected_batch(document_id)
        bookkeeping_agents = self.read_many(batch, self.read_bookkeeping_agent)

        return bookkeeping_agents

class InvestorRelationsDepartmentReader(CommonReader):
    """'fca_cia_aberta_dri_YYYY.csv'"""

    @classmethod
    def read_investor_relations_officer(cls, row: CSVRow) -> datatypes.InvestorRelationsOfficer:
        return datatypes.InvestorRelationsOfficer(
            type             = row.required('Tipo_Responsavel', datatypes.InvestorRelationsOfficerType),
            name             = row.required('Responsavel',      str),
            cpf              = row.required('CPF_Responsavel',  datatypes.CPF.from_zfilled_with_separators),
            address          = cls.read_address(row),
            contact          = cls.read_contact(row),
            activity_started = row.required('Data_Inicio_Atuacao', utils.date_from_string),
            activity_ended   = row.optional('Data_Fim_Atuacao',    utils.date_from_string)
        )

    def read(self, document_id: int) -> typing.List[datatypes.InvestorRelationsOfficer]:
        batch = self.read_expected_batch(document_id)
        ird   = self.read_many(batch, self.read_investor_relations_officer)

        return ird

class ShareholderDepartmentReader(CommonReader):
    """'fca_cia_aberta_departamento_acionistas_YYYY.csv'"""

    @classmethod
    def read_shareholder_dept_person(cls, row: CSVRow) -> datatypes.ShareholderDepartmentPerson:
        return datatypes.ShareholderDepartmentPerson(
            name             = row.required('Contato', str),
            address          = cls.read_address(row),
            contact          = cls.read_contact(row),
            activity_started = row.optional('Data_Inicio_Contato', utils.date_from_string),
            activity_ended   = row.optional('Data_Fim_Contato',    utils.date_from_string)
        )
    
    def read(self, document_id: int) -> typing.List[datatypes.ShareholderDepartmentPerson]:
        batch            = self.read_expected_batch(document_id)
        shareholder_dept = self.read_many(batch, self.read_shareholder_dept_person)

        return shareholder_dept

def fca_reader(archive: zipfile.ZipFile) -> typing.Generator[datatypes.FCA, None, None]:
    namelist = _MemberNameList(iter(archive.namelist()))

    with contextlib.ExitStack() as stack:
        def open_on_stack(filename: str):
            member = archive.open(filename, mode='r')
            stream = io.TextIOWrapper(member, encoding='iso-8859-1')
            
            return stack.enter_context(stream)

        head_reader              = RegularDocumentHeadReader        (open_on_stack(namelist.head_filename))
        address_reader           = AddressReader                    (open_on_stack(namelist.address_filename))
        trading_admission_reader = TradingAdmissionReader           (open_on_stack(namelist.foreign_country_filename))
        issuer_company_reader    = IssuerCompanyReader              (open_on_stack(namelist.general_filename))
        security_reader          = SecurityReader                   (open_on_stack(namelist.securities_filename))
        auditor_reader           = AuditorReader                    (open_on_stack(namelist.auditor_filename))
        bookkeeping_agent_reader = BookkeepingAgentReader           (open_on_stack(namelist.bookkeeper_filename))
        ird_reader               = InvestorRelationsDepartmentReader(open_on_stack(namelist.investor_relations_department_filename))
        shareholder_dept_reader  = ShareholderDepartmentReader      (open_on_stack(namelist.shareholder_department_filename))

        while True:
            try:
                head = head_reader.read()
            except StopIteration:
                break

            try:
                addresses = address_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                addresses = ()
            except exceptions.BadDocument as exc:
                print('Error while reading addresses:', exc)
                addresses = ()

            try:
                trading_admissions = trading_admission_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                trading_admissions = ()
            except exceptions.BadDocument as exc:
                print('Error while reading trading admissions:', exc)
                trading_admissions = ()

            try:
                issuer_company = issuer_company_reader.read(head.id, trading_admissions, addresses)
            except (UnexpectedBatch, StopIteration):
                issuer_company = None
            except exceptions.BadDocument as exc:
                print('Error while reading issuer company:', exc)
                issuer_company = None

            try:
                securities = security_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                securities = ()
            except exceptions.BadDocument as exc:
                print('Error while reading securities:', exc)
                securities = ()

            try:
                auditors = auditor_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                auditors = ()
            except exceptions.BadDocument as exc:
                print('Error while reading auditors:', exc)
                auditors = ()

            try:
                bookkeeping_agents = bookkeeping_agent_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                bookkeeping_agents = ()
            except exceptions.BadDocument as exc:
                print('Error while reading bookkeeping agents:', exc)
                bookkeeping_agents = ()
            
            try:
                ird = ird_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                ird = ()
            except exceptions.BadDocument as exc:
                print('Error while reading IRD:', exc)
                ird = ()

            try:
                shareholder_dept = shareholder_dept_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                shareholder_dept = ()
            except exceptions.BadDocument as exc:
                print('Error while reading shareholder department:', exc)
                shareholder_dept = ()

            yield datatypes.FCA(
                cnpj                          = head.cnpj,
                reference_date                = head.reference_date,
                version                       = head.version,
                company_name                  = head.company_name,
                cvm_code                      = head.cvm_code,
                type                          = head.type,
                id                            = head.id,
                receipt_date                  = head.receipt_date,
                url                           = head.url,
                issuer_company                = issuer_company,
                securities                    = tuple(securities),
                auditors                      = tuple(auditors),
                bookkeeping_agents            = tuple(bookkeeping_agents),
                investor_relations_department = tuple(ird),
                shareholder_department        = tuple(shareholder_dept)
            )

class FCAFile(zipfile.ZipFile):
    """Class for reading `FCA` objects from an FCA file."""

    def __init__(self, file: typing.Union[os.PathLike, typing.IO[bytes]]) -> None:
        super().__init__(file, mode='r')

        self._reader = fca_reader(archive=self)

    def __iter__(self) -> FCAFile:
        return self

    def __next__(self) -> datatypes.FCA:
        return next(self._reader)