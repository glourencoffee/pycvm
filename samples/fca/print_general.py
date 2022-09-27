import cvm
import sys
import time
import typing

def print_company(co: cvm.IssuerCompany):
    print('corporate_name:',             co.corporate_name)
    print('previous_corporate_name:',    co.previous_corporate_name)
    print('establishment_date:',         co.establishment_date)
    print('cvm_code:',                   co.cvm_code)
    print('registration_date:',          co.cvm_registration_date)
    print('registration_category:',      co.cvm_registration_category)
    print('registration_category_date:', co.cvm_registration_category_started)
    print('registration_status:',        co.cvm_registration_status)
    print('registration_status_date:',   co.cvm_registration_status_started)
    print('home_country:',               co.home_country)
    print('securities_custody_country:', co.securities_custody_country)
    print('industry:',                   co.industry)

def print_security(sec: cvm.Security):
    print('  {')
    print('    type:',                          sec.type)
    print('    market_type:',                   sec.market_type)
    print('    market_managing_entity_symbol:', sec.market_managing_entity_symbol)
    print('    market_managing_entity_name:',   sec.market_managing_entity_name)
    print('    preferred_share_type:',          sec.preferred_share_type)
    print('    bdr_unit_composition:',          sec.bdr_unit_composition)
    print('    trading_symbol:',                sec.trading_symbol)
    print('    trading_started:',               sec.trading_started)
    print('    trading_ended:',                 sec.trading_ended)
    print('    market_segment:',                sec.market_segment)
    print('    listing_started:',               sec.listing_started)
    print('    listing_ended:',                 sec.listing_ended)
    print('  }')

def print_auditor(auditor: cvm.Auditor):
    print('  {')
    print('    name:',                               auditor.name)
    print('    tax_id:',                             auditor.tax_id)
    print('    cvm_code:',                           auditor.cvm_code)
    print('    activity_started:',                   auditor.activity_started)
    print('    activity_ended:',                     auditor.activity_ended)
    print('    technical_manager_name:',             auditor.technical_manager_name)
    print('    technical_manager_cpf:',              auditor.technical_manager_cpf)
    print('    technical_manager_activity_started:', auditor.technical_manager_activity_started)
    print('    technical_manager_activity_ended:',   auditor.technical_manager_activity_ended)
    print('  }')

def print_bookkeeping_agent(agent: cvm.BookkeepingAgent):
    print('  {')
    print('    name:',             agent.name)
    print('    cnpj:',             agent.cnpj)
    print('    address:',          agent.address)
    print('    contact:',          agent.contact)
    print('    activity_started:', agent.activity_started)
    print('    activity_ended:',   agent.activity_ended)
    print('  }')

def print_ird_officer(officer: cvm.InvestorRelationsOfficer):
    print('  {')
    print('    type:',             officer.type)
    print('    name:',             officer.name)
    print('    cpf:',              officer.cpf)
    print('    address:',          officer.address)
    print('    contact:',          officer.contact)
    print('    activity_started:', officer.activity_started)
    print('    activity_ended:',   officer.activity_ended)
    print('  }')

def print_shareholder_dept_person(person: cvm.ShareholderDepartmentPerson):
    print('  {')
    print('    name:',             person.name)
    print('    address:',          person.address)
    print('    contact:',          person.contact)
    print('    activity_started:', person.activity_started)
    print('    activity_ended:',   person.activity_ended)
    print('  }')

def print_list(text: str, l: list, item_printer: typing.Callable[[typing.Any], None]):
    print(text, ': ', sep='', end='')

    if len(l) == 0:
        print('None')
        return

    print('[')

    for item in l:
        item_printer(item)
    
    print(']')

def print_fca(fca: cvm.FCA):
    print('-----------------')
    print(fca.cnpj, '/', fca.company_name, 'version', fca.version)

    if fca.issuer_company is not None:
        print_company(fca.issuer_company)

    print_list('Securities',               fca.securities,                    print_security)
    print_list('Auditors',                 fca.auditors,                      print_auditor)
    print_list('Bookkeeping Agents',       fca.bookkeeping_agents,            print_bookkeeping_agent)
    print_list('Investors Relation Dept.', fca.investor_relations_department, print_ird_officer)
    print_list('Shareholder Dept.',        fca.shareholder_department,        print_shareholder_dept_person)

def main():
    if len(sys.argv) < 2:
        print('usage: print_general.py <fca>')
        return 1

    try:
        for fca in cvm.fca_reader(sys.argv[1]):
            print_fca(fca)
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    return 0

if __name__ == '__main__':
    sys.exit(main())