import collections
import datetime
import cvm
import dataclasses
import os
import sys
import typing
import zlib

@dataclasses.dataclass
class Company:
    cvm_code: str
    name: str
    version: int
    reference_date: datetime.date

@dataclasses.dataclass
class AccountLayout:
    fixed_accounts: typing.List[cvm.Account] = dataclasses.field(default_factory=list)
    companies:      typing.List[Company]     = dataclasses.field(default_factory=list)

def get_account_layouts(dfp_file: cvm.DFPITRFile,
                        max_level: int,
                        statement_type: cvm.StatementType
) -> typing.Dict[int, AccountLayout]:
    
    layouts = collections.defaultdict(AccountLayout)

    for doc in dfp_file:
        if doc.consolidated is None:
            continue

        print("reading consolidated BPA layout by company '", doc.company_name, "'", sep='')

        fixed_accounts = []
        layout_hash    = ''
        statement      = doc.consolidated.last[statement_type]

        for acc in statement.accounts:
            if acc.is_fixed and acc.level <= max_level:
                fixed_accounts.append(acc)
                layout_hash += acc.code + acc.name

        layout_hash = zlib.crc32(layout_hash.encode('utf-8'))

        company = Company(
            cvm_code       = doc.cvm_code,
            name           = doc.company_name,
            version        = doc.version,
            reference_date = doc.reference_date
        )

        layout = layouts[layout_hash]
        layout.fixed_accounts = fixed_accounts
        layout.companies.append(company)

    return layouts

def write_layout(file: typing.IO, layout_hash: int, layout: AccountLayout) -> None:
    accounts  = layout.fixed_accounts
    companies = layout.companies

    file.write('-------------------------\n')
    file.write(f'{ layout_hash }:\n')

    file.write(f'accounts ({len(accounts)}):\n')

    for acc in accounts:
        file.write(f' - {acc.code} - {acc.name}\n')

    file.write(f'companies ({len(companies)}):\n')

    for co in companies:
        file.write(f'{co.cvm_code} - {co.name} - ref. date({co.reference_date}) version({co.version})\n')

def write_layouts(out_dir_name: str, layouts: typing.Dict[int, AccountLayout]) -> None:
    for i, (layout_hash, layout) in enumerate(layouts.items()):
        out_file_path = os.path.join(out_dir_name, str(i) + '.txt')

        with open(out_file_path, 'w', encoding='utf-8') as out_file:
            print("info: writing layout to '", out_file_path, "'", sep='')
            write_layout(out_file, layout_hash, layout)

def main():
    if len(sys.argv) < 5:
        print('usage: count_account_layouts.py <dfp-file> <out-dir> <max-level> <statement-type>')
        return 1

    dfp_file_name = sys.argv[1]
    out_dir_name  = sys.argv[2]

    try:
        max_level = int(sys.argv[3])
    except ValueError as exc:
        print('error: max-level is not a valid number:', exc)
        return 1

    if max_level < 1:
        print('error: max-level must be greater than zero (got: ', max_level, ')', sep='')
        return 1

    statement_type = sys.argv[4].upper()

    if statement_type not in ('BPA', 'BPP', 'DRE'):
        print('error: invalid/unsupported statement type:', statement_type)
        return 1

    statement_type = getattr(cvm.StatementType, statement_type)

    with cvm.DFPITRFile(dfp_file_name) as file:
        layouts = get_account_layouts(file, max_level, statement_type)

    if not os.path.isdir(out_dir_name):
        os.mkdir(out_dir_name)

    write_layouts(out_dir_name, layouts)

    return 0

if __name__ == '__main__':
    sys.exit(main())