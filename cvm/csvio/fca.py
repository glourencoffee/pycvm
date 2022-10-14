from __future__ import annotations
import contextlib
import functools
import io
import os
import typing
import zipfile
from cvm                import datatypes, exceptions, utils
from cvm.csvio.member   import MemberNameList
from cvm.csvio.row      import CSVRow
from cvm.csvio.batch    import CSVBatch
from cvm.csvio.document import RegularDocumentHeadReader, RegularDocumentBodyReader, UnexpectedBatch
from cvm.utils          import open_zip_member_on_stack
from cvm.datatypes      import (
    ControllingInterest, SecurityType,
    MarketType, MarketSegment, PreferredShareType,
    InvestorRelationsOfficerType, IssuerStatus,
    RegistrationCategory, RegistrationStatus,
    Industry
)

__all__ = [
    'fca_reader',
    'FCAFile'
]

class FCAMemberNameList(MemberNameList):
    head: str
    auditor: str
    dissemination_channel: str
    shareholder_department: str
    investor_relations_department: str
    address: str
    bookkeeper: str
    general: str
    foreign_country: str
    securities: str

    @classmethod
    def attribute_mapping(cls) -> typing.Dict[str, str]:
        return {
            '':                             'head',
            '_auditor':                     'auditor',
            '_canal_divulgacao':            'dissemination_channel',
            '_departamento_acionistas':     'shareholder_department',
            '_dri':                         'investor_relations_department',
            '_endereco':                    'address',
            '_escriturador':                'bookkeeper',
            '_geral':                       'general',
            '_pais_estrangeiro_negociacao': 'foreign_country',
            '_valor_mobiliario':            'securities',
        }

    __slots__ = (
        'head',
        'auditor',
        'dissemination_channel',
        'shareholder_department',
        'investor_relations_department',
        'address',
        'bookkeeper',
        'general',
        'foreign_country',
        'securities',
    )

class CommonReader(RegularDocumentBodyReader):
    @staticmethod
    @functools.lru_cache
    def countries() -> typing.Dict[str, str]:
        return {
            'Afeganistão': 'AF',
            'África do Sul': 'ZA',
            'Albânia': 'AL',
            'Alemanha': 'DE',
            'Algéria': 'DZ',
            'Andorra': 'AD',
            'Angola': 'AO',
            'Anguilla': 'AI',
            'Antártida': 'AQ',
            'Antígua e Barbuda': 'AG',
            'Antilhas Holandesas': 'AN',
            'Arábia Saudita': 'SA',
            'Argentina': 'AR',
            'Armênia': 'AM',
            'Aruba': 'AW',
            'Austrália': 'AU',
            'Áustria': 'AT',
            'Azerbaijão': 'AZ',
            'Bahamas': 'BS',
            'Bahrein': 'BH',
            'Bangladesh': 'BD',
            'Barbados': 'BB',
            'Belarus': 'BY',
            'Bélgica': 'BE',
            'Belize': 'BZ',
            'Benin': 'BJ',
            'Bermudas': 'BM',
            'Bolívia': 'BO',
            'Bósnia-Herzegóvina': 'BA',
            'Botsuana': 'BW',
            'Brasil': 'BR',
            'Brunei': 'BN',
            'Bulgária': 'BG',
            'Burkina Fasso': 'BF',
            'Burundi': 'BI',
            'Butão': 'BT',
            'Cabo Verde': 'CV',
            'Camarões': 'CM',
            'Camboja': 'KH',
            'Canadá': 'CA',
            'Cazaquistão': 'KZ',
            'Chade': 'TD',
            'Chile': 'CL',
            'China': 'CN',
            'Chipre': 'CY',
            'Singapura': 'SG',
            'Colômbia': 'CO',
            'Congo': 'CG',
            'Coréia do Norte': 'KP',
            'Coréia do Sul': 'KR',
            'Costa do Marfim': 'CI',
            'Costa Rica': 'CR',
            'Croácia (Hrvatska)': 'HR',
            'Cuba': 'CU',
            'Dinamarca': 'DK',
            'Djibuti': 'DJ',
            'Dominica': 'DM',
            'Egito': 'EG',
            'El Salvador': 'SV',
            'Emirados Árabes Unidos': 'AE',
            'Equador': 'EC',
            'Eritréia': 'ER',
            'Eslováquia': 'SK',
            'Eslovênia': 'SI',
            'Espanha': 'ES',
            'Estados Unidos': 'US',
            'Estônia': 'EE',
            'Etiópia': 'ET',
            'Federação Russa': 'RU',
            'Fiji': 'FJ',
            'Filipinas': 'PH',
            'Finlândia': 'FI',
            'França': 'FR',
            'França Metropolitana': 'FX',
            'Gabão': 'GA',
            'Gâmbia': 'GM',
            'Gana': 'GH',
            'Geórgia': 'GE',
            'Gibraltar': 'GI',
            'Grã-Bretanha (Reino Unido, UK)': 'GB',
            'Granada': 'GD',
            'Grécia': 'GR',
            'Groelândia': 'GL',
            'Guadalupe': 'GP',
            'Guam (Território dos Estados Unidos)': 'GU',
            'Guatemala': 'GT',
            'Guiana': 'GY',
            'Guiana Francesa': 'GF',
            'Guiné': 'GN',
            'Guiné Equatorial': 'GQ',
            'Guiné-Bissau': 'GW',
            'Haiti': 'HT',
            'Holanda': 'NL',
            'Honduras': 'HN',
            'Hong Kong': 'HK',
            'Hungria': 'HU',
            'Iêmen': 'YE',
            'Ilha Bouvet (Território da Noruega)': 'BV',
            'Ilha Natal': 'CX',
            'Ilha Pitcairn': 'PN',
            'Ilha Reunião': 'RE',
            'Ilhas Cayman': 'KY',
            'Ilhas Cocos': 'CC',
            'Ilhas Comores': 'KM',
            'Ilhas Cook': 'CK',
            'Ilhas Faeroes': 'FO',
            'Ilhas Falkland (Malvinas)': 'FK',
            'Ilhas Geórgia do Sul e Sandwich do Sul': 'GS',
            'Ilhas Heard e McDonald (Território da Austrália)': 'HM',
            'Ilhas Marianas do Norte': 'MP',
            'Ilhas Marshall': 'MH',
            'Ilhas Menores dos Estados Unidos': 'UM',
            'Ilhas Norfolk': 'NF',
            'Ilhas Seychelles': 'SC',
            'Ilhas Solomão': 'SB',
            'Ilhas Svalbard e Jan Mayen': 'SJ',
            'Ilhas Tokelau': 'TK',
            'Ilhas Turks e Caicos': 'TC',
            'Ilhas Virgens (Estados Unidos)': 'VI',
            'Ilhas Virgens (Britânicas)': 'VG',
            'Ilhas Wallis e Futuna': 'WF',
            'índia': 'IN',
            'Indonésia': 'ID',
            'Irã': 'IR',
            'Iraque': 'IQ',
            'Irlanda': 'IE',
            'Islândia': 'IS',
            'Israel': 'IL',
            'Itália': 'IT',
            'Iugoslávia': 'YU',
            'Jamaica': 'JM',
            'Japão': 'JP',
            'Jordânia': 'JO',
            'Kênia': 'KE',
            'Kiribati': 'KI',
            'Kuait': 'KW',
            'Laos': 'LA',
            'Látvia': 'LV',
            'Lesoto': 'LS',
            'Líbano': 'LB',
            'Libéria': 'LR',
            'Líbia': 'LY',
            'Liechtenstein': 'LI',
            'Lituânia': 'LT',
            'Luxemburgo': 'LU',
            'Macau': 'MO',
            'Macedônia': 'MK',
            'Madagascar': 'MG',
            'Malásia': 'MY',
            'Malaui': 'MW',
            'Maldivas': 'MV',
            'Mali': 'ML',
            'Malta': 'MT',
            'Marrocos': 'MA',
            'Martinica': 'MQ',
            'Maurício': 'MU',
            'Mauritânia': 'MR',
            'Mayotte': 'YT',
            'México': 'MX',
            'Micronésia': 'FM',
            'Moçambique': 'MZ',
            'Moldova': 'MD',
            'Mônaco': 'MC',
            'Mongólia': 'MN',
            'Montserrat': 'MS',
            'Myanma': 'MM',
            'Namíbia': 'NA',
            'Nauru': 'NR',
            'Nepal': 'NP',
            'Nicarágua': 'NI',
            'Níger': 'NE',
            'Nigéria': 'NG',
            'Niue': 'NU',
            'Noruega': 'NO',
            'Nova Caledônia': 'NC',
            'Nova Zelândia': 'NZ',
            'Omã': 'OM',
            'Palau': 'PW',
            'Panamá': 'PA',
            'Papua-Nova Guiné': 'PG',
            'Paquistão': 'PK',
            'Paraguai': 'PY',
            'Peru': 'PE',
            'Polinésia Francesa': 'PF',
            'Polônia': 'PL',
            'Porto Rico': 'PR',
            'Portugal': 'PT',
            'Qatar': 'QA',
            'Quirguistão': 'KG',
            'República Centro-Africana': 'CF',
            'República Dominicana': 'DO',
            'República Tcheca': 'CZ',
            'Romênia': 'RO',
            'Ruanda': 'RW',
            'Saara Ocidental': 'EH',
            'Saint Vincente e Granadinas': 'VC',
            'Samoa Ocidental': 'AS',
            'Samoa Ocidental': 'WS',
            'San Marino': 'SM',
            'Santa Helena': 'SH',
            'Santa Lúcia': 'LC',
            'São Cristóvão e Névis': 'KN',
            'São Tomé e Príncipe': 'ST',
            'Senegal': 'SN',
            'Serra Leoa': 'SL',
            'Síria': 'SY',
            'Somália': 'SO',
            'Sri Lanka': 'LK',
            'St. Pierre and Miquelon': 'PM',
            'Suazilândia': 'SZ',
            'Sudão': 'SD',
            'Suécia': 'SE',
            'Suíça': 'CH',
            'Suriname': 'SR',
            'Tadjiquistão': 'TJ',
            'Tailândia': 'TH',
            'Taiwan': 'TW',
            'Tanzânia': 'TZ',
            'Território Britânico do Oceano índico': 'IO',
            'Territórios do Sul da França': 'TF',
            'Timor Leste': 'TP',
            'Togo': 'TG',
            'Tonga': 'TO',
            'Trinidad and Tobago': 'TT',
            'Tunísia': 'TN',
            'Turcomenistão': 'TM',
            'Turquia': 'TR',
            'Tuvalu': 'TV',
            'Ucrânia': 'UA',
            'Uganda': 'UG',
            'Uruguai': 'UY',
            'Uzbequistão': 'UZ',
            'Vanuatu': 'VU',
            'Vaticano': 'VA',
            'Venezuela': 'VE',
            'Vietnã': 'VN',
            'Zaire': 'ZR',
            'Zâmbia': 'ZM',
            'Zimbábue': 'ZW',

            #===========================================================
            # Typos, mistakes, and alternatives (see issue #12)
            #
            # Below is what happens when you don't enforce valid country
            # names at GUI level, but instead let user type out country
            # names and accept them as is. Argh.
            #===========================================================
            
            # Brazil
            'Brasi': 'BR',
            'BR': 'BR',
            'São Paulo': 'BR',

            # Spain
            'Espanhã': 'ES',

            # Great Britain (United Kingdom)
            'Reino Unido': 'GB',
            'Inglaterra': 'GB',

            # United States
            'Nova Iorque': 'US',
            'EUA': 'US',
            'Estados Unidos da América': 'US',

            # Luxembourg
            'Luxemburgo.': 'LU',

            # Canada
            'Canadá Toronto Stock Exchange Venture (TSX-V)': 'CA',

            # Switzerland
            'Suiça': 'CH',
        }

    @classmethod
    def read_country(cls, row: CSVRow, fieldname: str) -> typing.Optional[str]:
        country_name = row[fieldname]

        if country_name in ('', 'N/A', 'Não aplicável'):
            return None

        try:
            return cls.countries()[country_name]
        except KeyError:
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

    @staticmethod
    @functools.lru_cache
    def controlling_interests() -> typing.Dict[str, ControllingInterest]:
        return {
            'Estatal':              ControllingInterest.GOVERNMENTAL,
            'Estatal Holding':      ControllingInterest.GOVERNMENTAL_HOLDING,
            'Estrangeiro':          ControllingInterest.FOREIGN,
            'Estrangeiro Holding':  ControllingInterest.FOREIGN_HOLDING,
            'Privado':              ControllingInterest.PRIVATE,
            'Privado Holding':      ControllingInterest.PRIVATE_HOLDING,
        }

    @staticmethod
    @functools.lru_cache
    def issuer_statuses() -> typing.Dict[str, IssuerStatus]:
        return {
            'Fase Pré-Operacional':                   IssuerStatus.PRE_OPERATIONAL_PHASE,
            'Fase Operacional':                       IssuerStatus.OPERATIONAL_PHASE,
            'Em Recuperação Judicial ou Equivalente': IssuerStatus.JUDICIAL_RECOVERY_OR_EQUIVALENT,
            'Em Recuperação Extrajudicial':           IssuerStatus.EXTRAJUDICIAL_RECOVERY,
            'Em Falência':                            IssuerStatus.BANKRUPT,
            'Em Liquidação Extrajudicial':            IssuerStatus.EXTRAJUDICIAL_LIQUIDATION,
            'Em liquidação judicial':                 IssuerStatus.JUDICIAL_LIQUIDATION,
            'Paralisada':                             IssuerStatus.STALLED,
        }

    @staticmethod
    @functools.lru_cache
    def registration_categories() -> typing.Dict[str, RegistrationCategory]:
        return {
            'Categoria A': RegistrationCategory.A,
            'Categoria B': RegistrationCategory.B,
            'Não Identificado': RegistrationCategory.UNKNOWN,
        }

    @staticmethod
    @functools.lru_cache
    def registration_statuses() -> typing.Dict[str, RegistrationStatus]:
        return {
            'Ativo':         RegistrationStatus.ACTIVE,
            'Em análise':    RegistrationStatus.UNDER_ANALYSIS,
            'Não concedido': RegistrationStatus.NOT_GRANTED,
            'Suspenso':      RegistrationStatus.SUSPENDED,
            'Cancelada':     RegistrationStatus.CANCELED,
        }

    @staticmethod
    @functools.lru_cache
    def industries() -> typing.Dict[str, Industry]:
        return {
            'Petróleo e Gás':
                Industry.OIL_AND_GAS,

            'Petroquímicos e Borracha':
                Industry.PETROCHEMICAL_AND_RUBBER,

            'Extração Mineral':
                Industry.MINERAL_EXTRACTION,

            'Papel e Celulose':
                Industry.PULP_AND_PAPER,

            'Têxtil e Vestuário':
                Industry.TEXTILE_AND_CLOTHING,

            'Metalurgia e Siderurgia':
                Industry.METALLURGY_AND_STEELMAKING,

            'Máquinas, Equipamentos, Veículos e Peças':
                Industry.MACHINERY_EQUIPMENT_VEHICLE_AND_PARTS,

            'Farmacêutico e Higiene':
                Industry.PHARMACEUTICAL_AND_HYGIENE,

            'Bebidas e Fumo':
                Industry.BEVERAGES_AND_TOBACCO,

            'Gráficas e Editoras':
                Industry.PRINTERS_AND_PUBLISHERS,

            'Construção Civil, Mat. Constr. e Decoração':
                Industry.CIVIL_CONSTRUCTION_BUILDING_AND_DECORATION_MATERIALS,

            'Energia Elétrica':
                Industry.ELETRICITY,

            'Telecomunicações':
                Industry.TELECOMMUNICATIONS,

            'Serviços Transporte e Logística':
                Industry.TRANSPORT_AND_LOGISTICS_SERVICES,

            'Comunicação e Informática':
                Industry.COMMUNICATION_AND_INFORMATION_TECHNOLOGY,

            'Saneamento, Serv. Água e Gás':
                Industry.SANITATION_WATER_AND_GAS_SERVICES,

            'Serviços médicos':
                Industry.MEDICAL_SERVICES,

            'Hospedagem e Turismo':
                Industry.HOSTING_AND_TOURISM,

            'Comércio (Atacado e Varejo)':
                Industry.WHOLESAIL_AND_RETAIL_COMMERCE,

            'Comércio Exterior':
                Industry.FOREIGN_COMMERCE,

            'Agricultura (Açúcar, Álcool e Cana)':
                Industry.AGRICULTURE,

            'Alimentos':
                Industry.FOOD,

            'Cooperativas':
                Industry.COOPERATIVES,

            'Bancos':
                Industry.BANKS,

            'Seguradoras e Corretoras':
                Industry.INSURANCE_AND_BROKERAGE_COMPANIES,

            'Arrendamento Mercantil':
                Industry.LEASING,

            'Previdência Privada':
                Industry.PRIVATE_PENSION,

            'Intermediação Financeira':
                Industry.FINANCIAL_INTERMEDIATION,

            'Factoring':
                Industry.FACTORING,

            'Crédito Imobiliário':
                Industry.REAL_ESTATE_CREDIT,

            'Reflorestamento':
                Industry.REFORESTATION,

            'Pesca':
                Industry.FISHING,

            'Embalagens':
                Industry.PACKAGING,

            'Educação':
                Industry.EDUCATION,

            'Securitização de Recebíveis':
                Industry.SECURITIZATION_OF_RECEIVABLES,

            'Brinquedos e Lazer':
                Industry.TOYS_AND_RECREATIONAL,

            'Bolsas de Valores/Mercadorias e Futuros':
                Industry.STOCK_EXCHANGES,

            # Enterprises, Administration, and Participation (EAP)
            'Emp. Adm. Part. - Petróleo e Gás':
                Industry.EAP_OIL_AND_GAS,

            'Emp. Adm. Part. - Petroquímicos e Borracha':
                Industry.EAP_PETROCHEMICAL_AND_RUBBER,

            'Emp. Adm. Part. - Extração Mineral':
                Industry.EAP_MINERAL_EXTRACTION,

            'Emp. Adm. Part. - Papel e Celulose':
                Industry.EAP_PULP_AND_PAPER,

            'Emp. Adm. Part. - Têxtil e Vestuário':
                Industry.EAP_TEXTILE_AND_CLOTHING,

            'Emp. Adm. Part. - Metalurgia e Siderurgia':
                Industry.EAP_METALLURGY_AND_STEELMAKING,

            'Emp. Adm. Part. - Máqs., Equip., Veíc. e Peças':
                Industry.EAP_MACHINERY_EQUIPMENT_VEHICLE_AND_PARTS,

            'Emp. Adm. Part. - Farmacêutico e Higiene':
                Industry.EAP_PHARMACEUTICAL_AND_HYGIENE,

            'Emp. Adm. Part. - Bebidas e Fumo':
                Industry.EAP_BEVERAGES_AND_TOBACCO,

            'Emp. Adm. Part. - Gráficas e Editoras':
                Industry.EAP_PRINTERS_AND_PUBLISHERS,

            'Emp. Adm. Part. - Const. Civil, Mat. Const. e Decoração':
                Industry.EAP_CIVIL_CONSTRUCTION_BUILDING_AND_DECORATION_MATERIALS,

            'Emp. Adm. Part. - Energia Elétrica':
                Industry.EAP_ELETRICITY,

            'Emp. Adm. Part. - Telecomunicações':
                Industry.EAP_TELECOMMUNICATIONS,

            'Emp. Adm. Part. - Serviços Transporte e Logística':
                Industry.EAP_TRANSPORT_AND_LOGISTICS_SERVICES,

            'Emp. Adm. Part. - Comunicação e Informática':
                Industry.EAP_COMMUNICATION_AND_INFORMATION_TECHNOLOGY,

            'Emp. Adm. Part. - Saneamento, Serv. Água e Gás':
                Industry.EAP_SANITATION_WATER_AND_GAS_SERVICES,

            'Emp. Adm. Part. - Serviços médicos':
                Industry.EAP_MEDICAL_SERVICES,

            'Emp. Adm. Part. - Hospedagem e Turismo':
                Industry.EAP_HOSTING_AND_TOURISM,

            'Emp. Adm. Part. - Comércio (Atacado e Varejo)':
                Industry.EAP_WHOLESAIL_AND_RETAIL_COMMERCE,

            'Emp. Adm. Part. - Comércio Exterior':
                Industry.EAP_FOREIGN_COMMERCE,

            'Emp. Adm. Part. - Agricultura (Açúcar, Álcool e Cana)':
                Industry.EAP_AGRICULTURE,

            'Emp. Adm. Part. - Alimentos':
                Industry.EAP_FOOD,

            'Emp. Adm. Part. - Cooperativas':
                Industry.EAP_COOPERATIVES,

            'Emp. Adm. Part. - Bancos':
                Industry.EAP_BANKS,

            'Emp. Adm. Part. - Seguradoras e Corretoras':
                Industry.EAP_INSURANCE_AND_BROKERAGE_COMPANIES,

            'Emp. Adm. Part. - Arrendamento Mercantil':
                Industry.EAP_LEASING,

            'Emp. Adm. Part. - Previdência Privada':
                Industry.EAP_PRIVATE_PENSION,

            'Emp. Adm. Part. - Intermediação Financeira':
                Industry.EAP_FINANCIAL_INTERMEDIATION,

            'Emp. Adm. Part. - Factoring':
                Industry.EAP_FACTORING,

            'Emp. Adm. Part. - Crédito Imobiliário':
                Industry.EAP_REAL_ESTATE_CREDIT,

            'Emp. Adm. Part. - Reflorestamento':
                Industry.EAP_REFORESTATION,

            'Emp. Adm. Part. - Pesca':
                Industry.EAP_FISHING,

            'Emp. Adm. Part. - Embalagens':
                Industry.EAP_PACKAGING,

            'Emp. Adm. Part. - Educação':
                Industry.EAP_EDUCATION,

            'Emp. Adm. Part. - Securitização de Recebíveis':
                Industry.EAP_SECURITIZATION_OF_RECEIVABLES,

            'Emp. Adm. Part. - Brinquedos e Lazer':
                Industry.EAP_TOYS_AND_RECREATIONAL,

            'Emp. Adm. Part.-Bolsas de Valores/Mercadorias e Futuros':
                Industry.EAP_STOCK_EXCHANGES,

            'Emp. Adm. Part. - Sem Setor Principal':
                Industry.EAP_NO_CORE_BUSINESS,

            # Old descriptions
            'Serviços Diversos':
                Industry.MISCELLANEOUS_SERVICES,

            'Emp. Adm. Participações':
                Industry.EAP,

            'Outras Atividades Industriais':
                Industry.OTHER_INDUSTRIAL_ACTIVITIES,

            'Serviços em Geral':
                Industry.GENERAL_SERVICES,
        }

    @classmethod
    def make_controlling_interest(cls, value: str) -> ControllingInterest:
        return cls.controlling_interests()[value]

    @classmethod
    def make_issuer_status(cls, value: str) -> IssuerStatus:
        return cls.issuer_statuses()[value]

    @classmethod
    def make_registration_category(cls, value: str) -> RegistrationCategory:
        return cls.registration_categories()[value]

    @classmethod
    def make_registration_status(cls, value: str) -> RegistrationStatus:
        return cls.registration_statuses()[value]

    @classmethod
    def make_industry(cls, value: str) -> Industry:
        return cls.industries()[value]

    def read(self,
             document_id: int,
             trading_admissions: typing.List[datatypes.TradingAdmission],
             addresses: typing.List[datatypes.Address]
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
            cvm_registration_category         = row.required('Categoria_Registro_CVM',            self.make_registration_category),
            cvm_registration_category_started = row.required('Data_Categoria_Registro_CVM',       utils.date_from_string),
            cvm_registration_status           = row.required('Situacao_Registro_CVM',             self.make_registration_status),
            cvm_registration_status_started   = row.required('Data_Situacao_Registro_CVM',        utils.date_from_string),
            home_country                      = self.read_country(row, 'Pais_Origem'),
            securities_custody_country        = self.read_country(row, 'Pais_Custodia_Valores_Mobiliarios'),
            trading_admissions                = trading_admissions,
            industry                          = row.required('Setor_Atividade',                   self.make_industry),
            issuer_status                     = row.required('Situacao_Emissor',                  self.make_issuer_status),
            issuer_status_started             = row.required('Data_Situacao_Emissor',             utils.date_from_string),
            controlling_interest              = row.required('Especie_Controle_Acionario',        self.make_controlling_interest),
            controlling_interest_last_changed = row.optional('Data_Especie_Controle_Acionario',   utils.date_from_string),
            fiscal_year_end_day               = row.required('Dia_Encerramento_Exercicio_Social', int),
            fiscal_year_end_month             = row.required('Mes_Encerramento_Exercicio_Social', int),
            fiscal_year_last_changed          = row.optional('Data_Alteracao_Exercicio_Social',   utils.date_from_string),
            webpage                           = row.optional('Pagina_Web',                        str),
            communication_channels            = [],  # TODO
            addresses                         = addresses,
            contact                           = None # TODO
        )

class SecurityReader(CommonReader):
    """'fca_cia_aberta_valor_mobiliario_YYYY.csv'"""

    @staticmethod
    @functools.lru_cache
    def security_types() -> typing.Dict[str, SecurityType]:
        return {
            'Ações Ordinárias':                                  SecurityType.STOCK,
            'Debêntures':                                        SecurityType.DEBENTURE,
            'Debêntures Conversíveis':                           SecurityType.CONVERTIBLE_DEBENTURE,
            'Bônus de Subscrição':                               SecurityType.SUBCRIPTION_BONUS,
            'Nota Comercial':                                    SecurityType.PROMISSORY_NOTE,
            'Contrato de Investimento Coletivo':                 SecurityType.COLLECTIVE_INVESTMENT_CONTRACT,
            'Certificados de Depósito de Valores Mobiliários':   SecurityType.SECURITIES_DEPOSITORY_RECEIPT,
            'Certificados de depósito de valores mobiliários':   SecurityType.SECURITIES_DEPOSITORY_RECEIPT,
            'Certificados de Recebíveis Imobiliários':           SecurityType.REAL_ESTATE_RECEIVABLE_CERTIFICATE,
            'Certificado de Recebíveis do Agronegócio':          SecurityType.AGRIBUSINESS_RECEIVABLE_CERTIFICATE,
            'Título de Investimento Coletivo':                   SecurityType.COLLECTIVE_INVESTMENT_BOND,
            'Letras Financeiras':                                SecurityType.FINANCIAL_BILLS,
            'Valor Mobiliário Não Registrado':                   SecurityType.UNREGISTERED_SECURITY,
            'Units':                                             SecurityType.UNITS,
            'Ações Preferenciais':                               SecurityType.PREFERRED_SHARES,
        }

    
    @staticmethod
    @functools.lru_cache
    def market_types() -> typing.Dict[str, MarketType]:
        return {
            'Balcão Não-Organizado': MarketType.NON_ORGANIZED_OTC,
            'Balcão Organizado':     MarketType.ORGANIZED_OTC,
            'Bolsa':                 MarketType.STOCK_EXCHANGE,
        }
    
    @staticmethod
    @functools.lru_cache
    def market_segments() -> typing.Dict[str, MarketSegment]:
        return {
            'Novo Mercado':                      MarketSegment.NEW_MARKET,
            'Nível 1 de Governança Corporativa': MarketSegment.CORPORATE_GOVERNANCE_L1,
            'Nível 2 de Governança Corporativa': MarketSegment.CORPORATE_GOVERNANCE_L2,
            'Bovespa Mais':                      MarketSegment.BOVESPA_PLUS,
            'Bovespa Mais N2':                   MarketSegment.BOVESPA_PLUS_L2,
        }

    @staticmethod
    @functools.lru_cache
    def preferred_share_types() -> typing.Dict[str, PreferredShareType]:
        return {
            'Preferencial Classe A': PreferredShareType.PNA,
            'Preferencial Classe B': PreferredShareType.PNB,
            'Preferencial Classe C': PreferredShareType.PNC,
            'Preferencial Classe U': PreferredShareType.PNU,
        }

    @classmethod
    def make_security_type(cls, value: str) -> SecurityType:
        return cls.security_types()[value]

    @classmethod
    def make_market_type(cls, value: str) -> MarketType:
        return cls.market_types()[value]

    @classmethod
    def make_market_segment(cls, value: str) -> MarketSegment:
        return cls.market_segments()[value]

    @classmethod
    def make_preferred_share_type(cls, value: str) -> PreferredShareType:
        return cls.preferred_share_types()[value]

    @classmethod
    def read_security(cls, row: CSVRow) -> datatypes.Security:
        return datatypes.Security(
            type                          = row.required('Valor_Mobiliario',              cls.make_security_type),
            market_type                   = row.required('Mercado',                       cls.make_market_type),
            market_managing_entity_symbol = row.required('Sigla_Entidade_Administradora', str),
            market_managing_entity_name   = row.required('Entidade_Administradora',       str),
            preferred_share_type          = row.optional('Classe_Acao_Preferencial',      cls.make_preferred_share_type, allow_empty_string=False),
            bdr_unit_composition          = row.optional('Composicao_BDR_Unit',           str),
            trading_symbol                = row.optional('Codigo_Negociacao',             str),
            trading_started               = row.optional('Data_Inicio_Negociacao',        utils.date_from_string),
            trading_ended                 = row.optional('Data_Fim_Negociacao',           utils.date_from_string),
            market_segment                = row.optional('Segmento',                      cls.make_market_segment, allow_empty_string=False),
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

    @staticmethod
    @functools.lru_cache
    def officer_types() -> typing.Dict[str, InvestorRelationsOfficerType]:
        return {
            'Diretor de Relações com Investidores':              InvestorRelationsOfficerType.INVESTOR_RELATIONS_OFFICER,
            'Liquidante':                                        InvestorRelationsOfficerType.LIQUIDATOR,
            'Administrador Judicial':                            InvestorRelationsOfficerType.JUDICIAL_ADMINISTRATOR,
            'Gestor Judicial':                                   InvestorRelationsOfficerType.TRUSTEE,
            'Síndico':                                           InvestorRelationsOfficerType.SYNDIC,
            'Representante Legal (para emissores estrangeiros)': InvestorRelationsOfficerType.LEGAL_REPRESENTATIVE,
            'Interventor':                                       InvestorRelationsOfficerType.INTERVENTOR,
            'Administrador Especial Temporário':                 InvestorRelationsOfficerType.SPECIAL_TEMP_ADMINISTRATOR,
            'Cargo Vago':                                        InvestorRelationsOfficerType.VACANT_POSITION,
        }

    @classmethod
    def make_officer_type(cls, value: str) -> InvestorRelationsOfficerType:
        return cls.officer_types()[value]

    @classmethod
    def read_investor_relations_officer(cls, row: CSVRow) -> datatypes.InvestorRelationsOfficer:
        return datatypes.InvestorRelationsOfficer(
            type             = row.required('Tipo_Responsavel', cls.make_officer_type),
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

def _reader(archive: zipfile.ZipFile, namelist: FCAMemberNameList) -> typing.Generator[datatypes.FCA, None, None]:
    with contextlib.ExitStack() as stack:
        head_reader              = RegularDocumentHeadReader        (open_zip_member_on_stack(stack, archive, namelist.head))
        address_reader           = AddressReader                    (open_zip_member_on_stack(stack, archive, namelist.address))
        trading_admission_reader = TradingAdmissionReader           (open_zip_member_on_stack(stack, archive, namelist.foreign_country))
        issuer_company_reader    = IssuerCompanyReader              (open_zip_member_on_stack(stack, archive, namelist.general))
        security_reader          = SecurityReader                   (open_zip_member_on_stack(stack, archive, namelist.securities))
        auditor_reader           = AuditorReader                    (open_zip_member_on_stack(stack, archive, namelist.auditor))
        bookkeeping_agent_reader = BookkeepingAgentReader           (open_zip_member_on_stack(stack, archive, namelist.bookkeeper))
        ird_reader               = InvestorRelationsDepartmentReader(open_zip_member_on_stack(stack, archive, namelist.investor_relations_department))
        shareholder_dept_reader  = ShareholderDepartmentReader      (open_zip_member_on_stack(stack, archive, namelist.shareholder_department))

        while True:
            try:
                head = head_reader.read()
            except StopIteration:
                break

            try:
                addresses = address_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                addresses = []
            except exceptions.BadDocument as exc:
                print('Error while reading addresses:', exc)
                addresses = []

            try:
                trading_admissions = trading_admission_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                trading_admissions = []
            except exceptions.BadDocument as exc:
                print('Error while reading trading admissions:', exc)
                trading_admissions = []

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
                securities = []
            except exceptions.BadDocument as exc:
                print('Error while reading securities:', exc)
                securities = []

            try:
                auditors = auditor_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                auditors = []
            except exceptions.BadDocument as exc:
                print('Error while reading auditors:', exc)
                auditors = []

            try:
                bookkeeping_agents = bookkeeping_agent_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                bookkeeping_agents = []
            except exceptions.BadDocument as exc:
                print('Error while reading bookkeeping agents:', exc)
                bookkeeping_agents = []
            
            try:
                ird = ird_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                ird = []
            except exceptions.BadDocument as exc:
                print('Error while reading IRD:', exc)
                ird = []

            try:
                shareholder_dept = shareholder_dept_reader.read(head.id)
            except (UnexpectedBatch, StopIteration):
                shareholder_dept = []
            except exceptions.BadDocument as exc:
                print('Error while reading shareholder department:', exc)
                shareholder_dept = []

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
                securities                    = securities,
                auditors                      = auditors,
                bookkeeping_agents            = bookkeeping_agents,
                investor_relations_department = ird,
                shareholder_department        = shareholder_dept
            )

def fca_reader(archive: zipfile.ZipFile) -> typing.Generator[datatypes.FCA, None, None]:
    namelist = FCAMemberNameList(iter(archive.namelist()))

    return _reader(archive, namelist)

class FCAFile(zipfile.ZipFile):
    """Class for reading `FCA` objects from an FCA file."""

    def __init__(self, file: typing.Union[os.PathLike, typing.IO[bytes]]) -> None:
        """Opens the FCA file in read mode."""

        super().__init__(file, mode='r')

        self._reader = fca_reader(archive=self)

    def __iter__(self) -> FCAFile:
        return self

    def __next__(self) -> datatypes.FCA:
        return next(self._reader)