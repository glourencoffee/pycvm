import zipfile
import sys
import cvm
import pandas as pd

def print_document(dfpitr: cvm.datatypes.DFPITR):
    print('=================================')
    print(dfpitr.company_name, ' (', dfpitr.reference_date, ', versão: ', dfpitr.version, ')', sep='')

    try:
        balance_sheet = cvm.balances.BalanceSheet.from_document(dfpitr)
        income_stmt   = cvm.balances.IncomeStatement.from_document(dfpitr)
        
        print()
        print('Balanço Patrimonial')
        print('-------------')
        print(pd.DataFrame([balance_sheet]).transpose().to_string(header=False))
        print()
        print('Demonstração de Resultado')
        print('----------------')
        print(pd.DataFrame([income_stmt]).transpose().to_string(header=False))
    except KeyError as exc:
        pass
    except cvm.exceptions.AccountLayoutError as exc:
        print('erro:', exc)

def main():
    if len(sys.argv) < 2:
        print('usage: print_balances.py <file>')

    try:
        with zipfile.ZipFile(sys.argv[1]) as file:
            for dfpitr in cvm.csvio.dfpitr_reader(file):
                print_document(dfpitr)

    except KeyboardInterrupt:
        pass

    return 0

if __name__ == '__main__':
    sys.exit(main())