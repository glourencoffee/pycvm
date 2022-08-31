import zipfile
import sys
import cvm
import pandas as pd

def print_dfpitr(dfpitr: cvm.datatypes.DFPITR):
    print('=================================')
    print(dfpitr.company_name, ' (', dfpitr.reference_date, ', versão: ', dfpitr.version, ')', sep='')

    if dfpitr.consolidated is None:
        print('o DFP/ITR não tem balanço consolidado')
        return

    try:
        balance_sheet = cvm.balances.BalanceSheet.from_dfpitr(dfpitr)
        income_stmt   = cvm.balances.IncomeStatement.from_dfpitr(dfpitr)
        
        print()
        print('Balanço Patrimonial')
        print('-------------')
        print(pd.DataFrame([balance_sheet]).transpose().to_string(header=False))
        print()
        print('Demonstração de Resultado')
        print('----------------')
        print(pd.DataFrame([income_stmt]).transpose().to_string(header=False))
    except cvm.exceptions.AccountLayoutError as exc:
        print('erro:', exc)

def main():
    if len(sys.argv) < 2:
        print('usage: print_balances.py <file>')

    try:
        with zipfile.ZipFile(sys.argv[1]) as file:
            for dfpitr in cvm.csvio.dfpitr_reader(file):
                print_dfpitr(dfpitr)

    except KeyboardInterrupt:
        pass

    return 0

if __name__ == '__main__':
    sys.exit(main())