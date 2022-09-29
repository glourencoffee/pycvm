import cvm
import sys
import time
import typing
import pandas as pd

def print_accounts(accounts: typing.List[cvm.Account]):
    columns = ['Código', 'Descrição', 'Quantidade', 'Fixa']
    data    = [(account.code, account.name, account.quantity, account.is_fixed) for account in accounts]
    df      = pd.DataFrame(data=data, columns=columns)

    print(df.to_string())

def print_collection(collection: cvm.StatementCollection):
    if collection.balance_type == cvm.BalanceType.CONSOLIDATED:
        consolidated_text = 'consolidado'
    else:
        consolidated_text = 'individual'

    print('---------------------')
    print('1 - BPA (', consolidated_text, '):', sep='')
    print_accounts(collection.bpa.normalized().accounts)

    print('---------------------')
    print('2 - BPP (', consolidated_text, '):', sep='')
    print_accounts(collection.bpp.normalized().accounts)

    print('---------------------')
    print('3 - DRE (', consolidated_text, '):', sep='')
    print_accounts(collection.dre.normalized().accounts)

def print_document(dfpitr: cvm.DFPITR):
    print('===============================================')
    print(dfpitr.company_name, ' (', dfpitr.reference_date, ') (versão: ', dfpitr.version, ')', sep='')

    for grouped_collection in dfpitr.grouped_collections():
        print_collection(grouped_collection.last)

def main():
    if len(sys.argv) < 2:
        print('usage: print_accounts.py <dfpitr>')
        return 1

    with cvm.DFPITRFile(sys.argv[1]) as file:
        for dfpitr in file:
            try:
                print_document(dfpitr)
                time.sleep(2)
            except KeyboardInterrupt:
                break

    return 0

if __name__ == '__main__':
    sys.exit(main())