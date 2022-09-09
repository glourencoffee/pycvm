from __future__ import annotations
import dataclasses
import decimal
import typing
from cvm import datatypes

@dataclasses.dataclass(init=True)
class BaseAccount:
    code: str
    name: str
    is_fixed: bool

    @property
    def level(self) -> int:
        return self.code.count('.') + 1

    __slots__ = (
        'code',
        'name',
        'is_fixed'
    )

@dataclasses.dataclass(init=True)
class Account(BaseAccount):
    quantity: decimal.Decimal
    
    __slots__ = (
        'quantity',
    )

@dataclasses.dataclass(init=True)
class DMPLAccount(BaseAccount):
    """Contains balances of an account in a `DMPL` statement."""

    share_capital: int
    """'Capital Social Integralizado'
    
    ### English

    Share capital is the money a company raises by issuing common or
    preferred stock. The amount of share capital or equity financing
    a company has can change over time with additional public offerings.[1]

    ### Portuguese

    Capital social é o dinheiro que uma companhia levanta emitindo
    ações preferenciais ou ordinárias. A quantidade de capital social
    ou de financiamento do patrimônio líquido que uma companhia tem
    pode mudar ao longo do tempo com outras ofertas públicas.

    ### Sources
    - [1]: https://www.investopedia.com/terms/s/sharecapital.asp
    """

    capital_reserve_and_treasury_shares: int
    """'Reservas de Capital, Opções Outorgadas e Ações em Tesouraria'
    
    ### English

    This attribute sums up three accounts of the balance sheet, namely
    capital reserve, options grants, and treasury shares, described
    as follows.

    Capital reserve is a reserve that is created out of capital profits.
    Capital profits are those profits arising out of those activity which
    are not part of the business operations, e.g. premium on issue of share
    and debentures, profits of sale of fixed asset, profit on redemption on
    debenture and profit on reissue of forfeited share and so on. [1]

    For businesses, a grant usually refers to the award of options on the
    company's stock given to an employee to elicit loyalty and incentivize
    strong job performance. After the waiting period, the employee can then
    exercise these stock options and take position of shares, often at a price
    below the market value of the stock at the time. Sometimes actual shares
    of stock are granted and can be sold after a waiting period. [2]
    
    Treasury stock, also known as treasury shares or reacquired stock, refers
    to previously outstanding stock that is bought back from stockholders by
    the issuing company. The result is that the total number of outstanding
    shares on the open market decreases. These shares are issued but no longer
    outstanding and are not included in the distribution of dividends or the
    calculation of earnings per share (EPS). [3]

    ### Português

    Este atributo soma três contas do balanço patrimonial, a saber, reservas
    de capital, opções outorgadas e ações em tesouraria, descritas a seguir.

    Reserva de capital é uma reserva que é criada a partir de lucros do capital.
    Lucros do capital são os lucros provenientes das atividades que não fazem
    parte das operações da companhia, por exemplo, prêmio na emissão de ações
    e debêntures, lucros em vendas de ativos fixos, lucro no resgate de
    debênture, lucro na reemissão de ações perdidas e assim por diante.

    Para empresas, uma outorga geralmente se refere à recompensa de opções de
    ações da companhia dado a um empregado para estimular lealdade e incentivar
    uma grande performance no trabalho. Após um período de espera, o empregado
    pode então exercer essas opções de ações e assumir a posição das ações,
    geralmente a um preço abaixo do valor de mercado da ação na época.
    Às vezes, ações reais são outorgadas e podem ser vendidas após um período
    de espera.

    Ações em tesouraria se referem às ações anteriormente em circulação que
    foram recompradas de acionistas pela companhia emissora. O resultado é que
    o número total de ações em circulação no mercado aberto é reduzido. Essas
    ações estão emitidas mas não mais em circulação, e não são inclusas na
    distribução de dividendos ou no cálculo de lucro por ação.

    ### Sources
    - [1]: https://byjus.com/question-answer/what-is-capital-reserve/
    - [2]: https://www.investopedia.com/terms/g/grant.asp
    - [3]: https://www.investopedia.com/terms/t/treasurystock.asp
    """

    profit_reserves: int
    """'Reservas de Lucro'
    
    ### English

    Profit reserves are reserve accounts that Brazilian public
    companies may have, as defined in Articles 193 to 197 of
    Law 6404/76. There are 6 profit reserve accounts:

    1. Legal Reserve
    2. Statutory Reserve
    3. Reserve for Contingencies
    4. Reserve of Tax Incentive
    5. Reserve of Income for Expansion (Reserve of Retained Earnings)
    6. Reserve of Unrealized Income

    Note that profit reserves are not exactly the same as appropriated
    retained earnings, since only item 5 of the above list describes
    retained earnings to be used for the particular purpose of
    reinvestment or expansion of the company.

    ### Português

    As reservas de lucros são contas de reserva que companhias
    brasileiras de capital aberto podem ter, como definido nos
    artigos 193 a 197 da Lei 6404/76. Existem 6 contas de reserva
    de lucro:

    1. Reserva Legal
    2. Reserva Estatutária
    3. Reserva para Contingência
    4. Reserva de Incentivo Fiscal
    5. Reserva de Lucros para Expansão (Reserva de Retenção de Lucro)
    6. Reserva de Lucros a Realizar

    Repare que as reservas de lucro não são exatamente a mesma coisa
    que a retenção de lucros, visto que apenas o item 5 da lista acima
    descreve uma apropriação de lucros para ser usado com o fim específico
    de reinvestimento ou expansão da companhia.
    """

    unappropriated_retained_earnings: int
    """'Lucros ou Prejuízos Acumulados'
    
    ### English
    
    Unappropriated retained earnings are part of the net income that
    a company has no specific use outlined for it yet. They may be
    appropriated into a profit reserve account or distributed as dividends.

    If the net income in a period is negative, that is, a deficit,
    the deficit must be absorbed by profit reserves.

    ### Português

    Resultados acumulados não apropriados são parte do lucro líquido
    para a qual uma companhia não planejou um uso específico ainda.
    Eles podem ser apropriados para uma conta de reserva de lucros
    ou distribuídos como dividendos.

    Se o lucro líquido do período for negativo, ou seja, um prejuízo,
    o prejuízo deve ser absorvido pelas reservas de lucro.
    """

    other_comprehensive_income: int
    """'Outros Resultados Abrangentes'
    
    ### English

    CVM defines comprehensive income as "a change that occurs in
    equity over a period that results from transactions and other
    events not derived from transactions with shareholders in
    their capacity of owners."

    ### Português

    A CVM define o resultado abrangente como "a mutação que ocorre no
    patrimônio líquido durante um período que resulta de transações e
    outros eventos que não derivados de transações com os sócios na
    sua qualidade de proprietários."
    """

    controlling_interest: int
    """'Patrimônio Líquido'
    
    ### English

    Controlling interest is the portion of equity ownership attributable
    to shareholders of the parent company.

    ### Português

    Participação controladora é a parte da participação acionária
    atribuível aos associonistas da companhia-mãe.
    """

    non_controlling_interest: typing.Optional[int]
    """'Participação dos Não Controladores'
    
    ### English

    Noncontrolling interest (NCI), also known as minority interest,
    is the portion of equity ownership in a subsidiary not attributable
    to the parent company, who has a controlling interest and consolidates
    the subsidiary's financial results with its own.

    This attribute is not None if an account pertains to a consolidated
    DMPL, and may be None if it pertains to an individual DMPL.

    ### Português

    Participação de não controladores, também conhecido como participação
    minoritária, é a parte da participação acionária em uma subsidiária
    não atribuível à companhia-mãe, que possui participação controladora
    e consolida os resultados financeiros da subsidiária com os seus próprios.

    Este attributo não é None se uma conta pertence a um DMPL consolidado,
    e pode ser None se ela pertence a um DMPL individual.
    """

    consolidated_equity: typing.Optional[int]
    """'Patrimônio Líquido Consolidado'
    
    ### English

    If an account pertains to an individual DMPL, this attribute is None.

    Otherwise, that account pertains to a consolidated DMPL and this
    attribute is the sum of controlling and non-controlling interests
    of that account, that is, `controlling_interest + non_controlling_interest`.

    ### Português

    Se uma conta pertence a um DMPL individual, este atributo é None.

    Caso contrário, a conta pertence a um DMPL consolidado e este atributo
    é a soma das participações controladora e não controladora da conta,
    ou seja, `controlling_interest + non_controlling_interest`.
    """

    __slots__ = (
        'share_capital',
        'capital_reserve_and_treasury_shares',
        'profit_reserves',
        'unappropriated_retained_earnings',
        'other_comprehensive_income',
        'controlling_interest',
        'non_controlling_interest',
        'consolidated_equity'
    )

class AccountTuple:
    __slots__ = ('_currency', '_currency_size', '_accounts')

    def __init__(self, currency: datatypes.Currency, currency_size: datatypes.CurrencySize, accounts: typing.Sequence[Account]):
        self._currency      = currency
        self._currency_size = currency_size
        self._accounts      = tuple(accounts)

    @property
    def currency(self) -> datatypes.Currency:
        return self._currency

    @property
    def currency_size(self) -> datatypes.CurrencySize:
        return self._currency_size

    def normalized(self) -> AccountTuple:
        """Returns a copy of `self` with `currency_size` normalized to `CurrencySize.UNIT`."""

        if self.currency_size == datatypes.CurrencySize.UNIT:
            return self
        else:
            if self.currency_size != datatypes.CurrencySize.THOUSAND:
                raise ValueError(f"unknown currency size '{self.currency_size}'")
            
            accounts   = []
            multiplier = 1000

            for code, name, quantity, is_fixed in self.items():
                accounts.append(Account(code, name, round(quantity * multiplier), is_fixed))

            return AccountTuple(self.currency, datatypes.CurrencySize.UNIT, accounts)

    def items(self) -> typing.Iterable[typing.Tuple[str, str, decimal.Decimal, bool]]:
        return ((acc.code, acc.name, acc.quantity, acc.is_fixed) for acc in self)

    def __iter__(self) -> typing.Iterator[Account]:
        return iter(self._accounts)

    def __getitem__(self, index: int) -> Account:
        return self._accounts[index]

class DMPLAccountTuple:
    __slots__ = ('_currency', '_currency_size', '_accounts')

    def __init__(self, currency: datatypes.Currency, currency_size: datatypes.CurrencySize, accounts: typing.Sequence[DMPLAccount]):
        self._currency      = currency
        self._currency_size = currency_size
        self._accounts      = tuple(accounts)

    @property
    def currency(self) -> datatypes.Currency:
        return self._currency

    @property
    def currency_size(self) -> datatypes.CurrencySize:
        return self._currency_size

    def normalized(self) -> DMPLAccountTuple:
        """Returns a copy of `self` with `currency_size` normalized to `CurrencySize.UNIT`."""

        if self.currency_size == datatypes.CurrencySize.UNIT:
            return self
        else:
            if self.currency_size != datatypes.CurrencySize.THOUSAND:
                raise ValueError(f"unknown currency size '{self.currency_size}'")
            
            accounts   = []
            multiplier = 1000

            def normalize(number: typing.Optional[int]) -> typing.Optional[int]:
                if number is None:
                    return
                
                return round(number * multiplier)

            for dmpl_account in self._accounts:
                normalized_dmpl_account = dataclasses.replace(
                    dmpl_account,
                    share_capital                       = normalize(dmpl_account.share_capital),
                    capital_reserve_and_treasury_shares = normalize(dmpl_account.capital_reserve_and_treasury_shares),
                    profit_reserves                     = normalize(dmpl_account.profit_reserves),
                    unappropriated_retained_earnings    = normalize(dmpl_account.unappropriated_retained_earnings),
                    other_comprehensive_income          = normalize(dmpl_account.other_comprehensive_income),
                    controlling_interest                = normalize(dmpl_account.controlling_interest),
                    non_controlling_interest            = normalize(dmpl_account.non_controlling_interest),
                    consolidated_equity                 = normalize(dmpl_account.consolidated_equity),
                )
                
                accounts.append(normalized_dmpl_account)

            return DMPLAccountTuple(self.currency, datatypes.CurrencySize.UNIT, accounts)

    def __iter__(self) -> typing.Iterator[DMPLAccount]:
        return iter(self._accounts)

    def __len__(self) -> int:
        return len(self._accounts)

    def __getitem__(self, index: int) -> DMPLAccount:
        return self._accounts[index]