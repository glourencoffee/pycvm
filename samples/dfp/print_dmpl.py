import cvm
import sys
import time
import pandas as pd

def print_dmpl(dmpl: cvm.DMPL):
    df = pd.DataFrame(data=dmpl.normalized().accounts)
    print(df)

def print_document(dfpitr: cvm.DFPITR):
    print('===============================================')
    print(dfpitr.company_name, ' (', dfpitr.reference_date, ') (versão: ', dfpitr.version, ', id: ', dfpitr.id, ')', sep='')

    for grouped_collection in dfpitr.grouped_collections():
        last = grouped_collection.last
        dmpl = last.dmpl

        if dmpl is not None:
            print('-------- DMPL (', last.balance_type.description, ') --------', sep='')
            print_dmpl(dmpl)

def main():
    if len(sys.argv) < 2:
        print('usage: print_dmpl.py <dfpitr>')
        return 1

    for dfpitr in cvm.dfpitr_reader(sys.argv[1]):
        try:
            print_document(dfpitr)
            time.sleep(2)
        except KeyboardInterrupt:
            break

    return 0

if __name__ == '__main__':
    sys.exit(main())