import csv
import pprint
import pandas as pd
from typing                             import TextIO, Generator, Optional
from datetime                           import date
from cvm.datatypes.cnpj                 import CNPJ
from cvm.datatypes.registration         import RegistrationCategory, RegistrationStatus
from cvm.datatypes.country              import Country
from cvm.datatypes.industry             import Industry
from cvm.datatypes.issuer_status        import IssuerStatus
from cvm.datatypes.controlling_interest import ControllingInterest
from cvm.parsing.util                   import read_optional, read_required, date_from_string, value_error_instantiator, dataframe_from_reader

class Document:
    cnpj: CNPJ
    reference_date: date
    version: int
    document_id: int
    corporate_name: str
    corporate_name_date: date
    prev_corporate_name: str
    establishment_date: date
    cvm_code: int
    registration_date: date
    registration_category: RegistrationCategory
    registration_category_date: date
    registration_status: RegistrationStatus
    registration_status_date: date
    home_country: Country
    securities_custody_country: Optional[Country]
    industry: Industry
    activity_description: str
    issuer_status: IssuerStatus
    issuer_status_date: date
    controlling_interest: ControllingInterest
    controlling_interest_date: date
    fiscal_year_closing_day: int
    fiscal_year_closing_month: int
    fiscal_year_change_date: date
    webpage: str

    def __repr__(self) -> str:
        return pprint.pformat(vars(self))

def _read_country(country: str) -> Optional:
    try:
        return Country(country)
    except ValueError:
        return None

def read_document(row) -> Document:
    doc = Document()
    doc.cnpj                       = read_required(row, 'CNPJ_Companhia',                    CNPJ)
    doc.reference_date             = read_required(row, 'Data_Referencia',                   date_from_string)
    doc.version                    = read_required(row, 'Versao',                            int)
    doc.document_id                = read_required(row, 'ID_Documento',                      int)
    doc.corporate_name             = read_required(row, 'Nome_Empresarial',                  str)
    doc.corporate_name_date        = read_optional(row, 'Data_Nome_Empresarial',             date_from_string)
    doc.prev_corporate_name        = read_optional(row, 'Nome_Empresarial_Anterior',         str)
    doc.establishment_date         = read_required(row, 'Data_Constituicao',                 date_from_string)
    doc.cvm_code                   = read_required(row, 'Codigo_CVM',                        int)
    doc.registration_date          = read_required(row, 'Data_Registro_CVM',                 date_from_string)
    doc.registration_category      = read_required(row, 'Categoria_Registro_CVM',            RegistrationCategory)
    doc.registration_category_date = read_required(row, 'Data_Categoria_Registro_CVM',       date_from_string)
    doc.registration_status        = read_required(row, 'Situacao_Registro_CVM',             RegistrationStatus)
    doc.registration_status_date   = read_required(row, 'Data_Situacao_Registro_CVM',        date_from_string)
    doc.home_country               = read_required(row, 'Pais_Origem',                       Country)
    doc.securities_custody_country = read_required(row, 'Pais_Custodia_Valores_Mobiliarios', value_error_instantiator(Country))
    doc.industry                   = read_required(row, 'Setor_Atividade',                   Industry)
    doc.activity_description       = read_optional(row, 'Descricao_Atividade',               str)
    doc.issuer_status              = read_optional(row, 'Situacao_Emissor',                  IssuerStatus)
    doc.issuer_status_date         = read_optional(row, 'Data_Situacao_Emissor',             date_from_string)
    doc.controlling_interest       = read_optional(row, 'Especie_Controle_Acionario',        ControllingInterest)
    doc.controlling_interest_date  = read_optional(row, 'Data_Especie_Controle_Acionario',   date_from_string)
    doc.fiscal_year_closing_day    = read_required(row, 'Dia_Encerramento_Exercicio_Social', int)
    doc.fiscal_year_closing_month  = read_required(row, 'Mes_Encerramento_Exercicio_Social', int)
    doc.fiscal_year_change_date    = read_optional(row, 'Data_Alteracao_Exercicio_Social',   date_from_string)
    doc.webpage                    = read_optional(row, 'Pagina_Web',                        str)

    return doc

def reader(csv_file: TextIO, delimiter: str = ';') -> Generator[Document, None, None]:
    csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

    for row in csv_reader:
        doc = read_document(row)
        yield doc

def read_dataframe(csv_file: TextIO, delimiter: str = ';') -> pd.DataFrame:
    return dataframe_from_reader(
        reader     = reader,
        csv_file   = csv_file,
        delimiter  = delimiter,
        attributes = [
            'cnpj',
            'reference_date',
            'version',
            'document_id',
            'corporate_name',
            'corporate_name_date',
            'prev_corporate_name',
            'establishment_date',
            'cvm_code',
            'registration_date',
            'registration_category',
            'registration_category_date',
            'registration_status',
            'registration_status_date',
            'home_country',
            'securities_custody_country',
            'industry',
            'activity_description',
            'issuer_status',
            'issuer_status_date',
            'controlling_interest',
            'controlling_interest_date',
            'fiscal_year_closing_day',
            'fiscal_year_closing_month',
            'fiscal_year_change_date',
            'webpage'
        ])