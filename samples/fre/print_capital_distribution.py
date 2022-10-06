import cvm
import sys
import time
import typing

def print_preferred_shares(preferred_shares: typing.Dict[cvm.PreferredShareType, cvm.PreferredShareDistribution]) -> None:
    for type, dist in preferred_shares.items():
        print('    - ', type, ': ', dist.count, ' (', dist.percent, '%)', sep='')

def print_capital_distribution(cd: cvm.CapitalDistribution) -> None:
    print(' - individual_shareholder_count: ',         cd.individual_shareholder_count,         sep='')
    print(' - corporation_shareholder_count: ',        cd.corporation_shareholder_count,        sep='')
    print(' - institutional_investor_count: ',         cd.institutional_investor_count,         sep='')
    print(' - outstanding_common_shares_count: ',      cd.outstanding_common_shares_count,      sep='')
    print(' - outstanding_common_shares_percent: ',    cd.outstanding_common_shares_percent,    sep='')
    print(' - outstanding_preferred_shares_count: ',   cd.outstanding_preferred_shares_count,   sep='')
    print(' - outstanding_preferred_shares_percent: ', cd.outstanding_preferred_shares_percent, sep='')
    print(' - outstanding_preferred_shares: [', sep='', end='')

    if len(cd.outstanding_preferred_shares) > 0:
        print()
        print_preferred_shares(cd.outstanding_preferred_shares)
        print(' ]')
    else:
        print(']')

    print(' - outstanding_shares_count: ',      cd.outstanding_shares_count,      sep='')
    print(' - outstanding_shares_percent: ',    cd.outstanding_shares_percent,    sep='')
    print(' - last_shareholder_meeting_date: ', cd.last_shareholder_meeting_date, sep='')

def print_fre(fre: cvm.FRE) -> None:
    print(fre)

    if fre.capital_distribution is not None:
        print_capital_distribution(fre.capital_distribution)

def main():
    if len(sys.argv) < 2:
        print('usage: print_general.py <fca> [sleep]')
        return 1

    try:
        sleep_sec = float(sys.argv[2])
    except (IndexError, ValueError):
        sleep_sec = 0.2

    try:
        with cvm.FREFile(sys.argv[1]) as file:
            for fre in file:
                print_fre(fre)
                time.sleep(sleep_sec)
    except KeyboardInterrupt:
        pass

    return 0

if __name__ == '__main__':
    sys.exit(main())