import zipfile
import sys
import cvm
import pandas as pd

missing_cvm_codes = []

def print_dfpitr(dfpitr: cvm.DFPITR):
    print('=================================')
    print(dfpitr.company_name, ' (', dfpitr.reference_date, ', versão: ', dfpitr.version, ')', sep='')

    if dfpitr.consolidated is None:
        print('o DFP/ITR não tem balanço consolidado')
        return

    try:
        balance_sheet = cvm.BalanceSheet.from_dfpitr(dfpitr)
        income_stmt   = cvm.IncomeStatement.from_dfpitr(dfpitr)
        
        print()
        print('Balanço Patrimonial')
        print('-------------')
        print(pd.DataFrame([balance_sheet]).transpose().to_string(header=False))
        print()
        print('Demonstração de Resultado')
        print('----------------')
        print(pd.DataFrame([income_stmt]).transpose().to_string(header=False))
    except cvm.AccountLayoutError as exc:
        print('erro:', exc)
    except ValueError as exc:
        print(exc)
        missing_cvm_codes.append(dfpitr.cvm_code)

def main():
    if len(sys.argv) < 2:
        print('usage: print_balances.py <file>')
        return 1

    try:
        with zipfile.ZipFile(sys.argv[1]) as file:
            for dfpitr in cvm.dfpitr_reader(file):
                print_dfpitr(dfpitr)

    except KeyboardInterrupt:
        pass
    else:
        if len(missing_cvm_codes) > 0:
            print('Could not generate balances for the following companies:')
        
            for cvm_code in missing_cvm_codes:
                print(cvm_code)

    return 0

if __name__ == '__main__':
    sys.exit(main())