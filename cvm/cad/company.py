from __future__ import annotations

import enum
import csv
import pprint
from typing           import Optional, TextIO, Generator
from datetime         import date
from cvm.parsing.util import cnpj_to_int, date_from_string, read_optional, read_required
from cvm.datatypes    import DescriptiveIntEnum, Phone, Address, AddressType, ControllingInterest, Manager, ManagerType

class MarketType(enum.Enum):
    EXCHANGE         = 'BOLSA'
    ORGANIZED_OTC    = 'BALCÃO ORGANIZADO'
    NONORGANIZED_OTC = 'BALCÃO NÃO ORGANIZADO'


class Auditor:
    name: str
    cnpj: int

class Company:
    cnpj: int
    corporate_name: str
    trade_name: Optional[str]
    cvm_code: int
    industry: Optional[Industry]
    registration_date: date
    registration_category: Optional[RegistrationCategory]
    establishment_date: Optional[date]
    cancelation_date: Optional[date]
    cancelation_reason: Optional[str]
    status: Status
    status_started: date
    market_type: Optional[MarketType]
    category_started: Optional[date]
    issuer_status: Optional[IssuerStatus]
    issuer_status_started: Optional[date]
    controlling_interest: ControllingInterest
    address: Address
    address_type: AddressType
    phone: Optional[Phone]
    fax: Optional[Phone]
    email: str
    manager: Optional[Manager]
    auditor: Optional[Auditor]

    def __str__(self) -> str:
        return pprint.pformat(vars(self))

def _read_optional_address(row, suffix: str = ''):
    zip_code = read_optional(row, 'CEP' + suffix, int)

    if zip_code is None:
        return None

    addr = Address()
    addr.zip_code   = zip_code
    addr.country    = read_optional(row, 'PAIS'       + suffix, str)
    addr.state      = read_required(row, 'UF'         + suffix, str)
    addr.county     = read_required(row, 'MUN'        + suffix, str)
    addr.district   = read_optional(row, 'BAIRRO'     + suffix, str)
    addr.street     = read_required(row, 'LOGRADOURO' + suffix, str)
    addr.complement = read_optional(row, 'COMPL'      + suffix, str)
    return addr

def _read_optional_phone(row, area_code_fieldname: str, number_fieldname: str) -> Optional[Phone]:
    area_code = read_optional(row, area_code_fieldname, str)
    number    = read_optional(row, number_fieldname,    str)

    if area_code is None or number is None:
        return None

    if area_code == 'RJ':
        area_code = 21
    else:
        area_code = int(area_code)

    localized_number = str(area_code) + str(number)
    
    try:
        phone = Phone()
        phone.area_code = int(localized_number[:2])
        phone.number    = int(localized_number[2:])
        return phone
    except ValueError:
        return None

def _read_optional_manager(row) -> Optional[Manager]:
    manager_type = read_optional(row, 'TP_RESP', ManagerType)

    if manager_type is None:
        return None

    manager = Manager()
    manager.type    = manager_type
    manager.name    = read_required(row, 'RESP',        str)
    manager.started = read_required(row, 'DT_INI_RESP', date_from_string)
    manager.address = _read_optional_address(row, suffix='_RESP')
    manager.phone   = _read_optional_phone(row, 'DDD_TEL_RESP', 'TEL_RESP')
    manager.fax     = _read_optional_phone(row, 'DDD_FAX_RESP', 'FAX_RESP')
    manager.email   = read_optional(row, 'EMAIL_RESP', str)

def _read_optional_auditor(row) -> Optional[Auditor]:
    cnpj = read_optional(row, 'CNPJ_AUDITOR', cnpj_to_int) 
    name = read_optional(row, 'AUDITOR',      str)

    if cnpj is None or name is None:
        return None

    auditor = Auditor()
    auditor.cnpj = cnpj
    auditor.name = name

    return auditor

def _read_company(row) -> Company:
    co = Company()
    co.cnpj                  = read_required(row, 'CNPJ_CIA',           cnpj_to_int)
    co.corporate_name        = read_required(row, 'DENOM_SOCIAL',       str)
    co.trade_name            = read_optional(row, 'DENOM_COMERC',       str)
    co.cvm_code              = read_required(row, 'CD_CVM',             int)
    co.industry              = read_optional(row, 'SETOR_ATIV',         Industry)
    co.registration_date     = read_required(row, 'DT_REG',             date_from_string)
    co.registration_category = read_optional(row, 'CATEG_REG',          RegistrationCategory)
    co.establishment_date    = read_optional(row, 'DT_CONST',           date_from_string)
    co.cancelation_date      = read_optional(row, 'DT_CANCEL',          date_from_string)
    co.cancelation_reason    = read_optional(row, 'MOTIVO_CANCEL',      str)
    co.status                = read_required(row, 'SIT',                Status)
    co.status_started        = read_required(row, 'DT_INI_SIT',         date_from_string)
    co.market_type           = read_optional(row, 'TP_MERC',            MarketType)
    co.category_started      = read_optional(row, 'DT_INI_CATEG',       date_from_string)
    co.issuer_status         = read_optional(row, 'SIT_EMISSOR',        IssuerStatus)
    co.issuer_status_started = read_optional(row, 'DT_INI_SIT_EMISSOR', date_from_string)
    co.controlling_interest  = read_required(row, 'CONTROLE_ACIONARIO', ControllingInterest)
    co.address               = _read_optional_address(row)
    co.address_type          = read_optional(row, 'TP_ENDER', AddressType)
    co.phone                 = _read_optional_phone(row, 'DDD_TEL', 'TEL')
    co.fax                   = _read_optional_phone(row, 'DDD_FAX', 'FAX')
    co.email                 = read_optional(row, 'EMAIL', str)
    co.manager               = _read_optional_manager(row)
    co.auditor               = _read_optional_auditor(row)
    
    return co

def reader(csv_file: TextIO, delimiter: str = ';') -> Generator[Company, None, None]:
    csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

    for row in csv_reader:
        try:
            co = _read_company(row)
            yield co
        except (KeyError) as exc:
            print('failed to read row:', exc)
            raise exc from None