import cvm
import sys
import time
import pandas as pd

def print_accounts(accounts: cvm.datatypes.AccountTuple):
    columns = ['Código', 'Descrição', 'Quantidade', 'Fixa']
    data    = [t for t in accounts.items()]
    df      = pd.DataFrame(data=data, columns=columns)

    print(df.to_string())

def print_collection(collection: cvm.datatypes.StatementCollection, consolidated_text: str):
    print('---------------------')
    print('1 - BPA (', consolidated_text, '):', sep='')
    print_accounts(collection.bpa.accounts.normalized())

    print('---------------------')
    print('2 - BPP (', consolidated_text, '):', sep='')
    print_accounts(collection.bpp.accounts.normalized())

    print('---------------------')
    print('3 - DRE (', consolidated_text, '):', sep='')
    print_accounts(collection.dre.accounts.normalized())

def print_document(dfpitr: cvm.datatypes.DFPITR):
    print('===============================================')
    print(dfpitr.company_name, ' (', dfpitr.reference_date, ') (versão: ', dfpitr.version, ')', sep='')

    last_fy = cvm.datatypes.FiscalYearOrder.LAST

    if len(dfpitr.individual) > 0:
        print_collection(dfpitr.individual[last_fy], 'individual')

    if len(dfpitr.consolidated) > 0:
        print_collection(dfpitr.consolidated[last_fy], 'consolidado')

def main():
    if len(sys.argv) < 2:
        print('usage: print_accounts.py <dfpitr>')
        return 1

    for dfpitr in cvm.csvio.dfpitr_reader(sys.argv[1]):
        try:
            print_document(dfpitr)
            time.sleep(2)
        except KeyboardInterrupt:
            break

    return 0

if __name__ == '__main__':
    sys.exit(main())