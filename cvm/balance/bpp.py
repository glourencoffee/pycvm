import dataclasses
import decimal
from cvm.balance.balance import Balance

@dataclasses.dataclass(init=True, frozen=True)
class IndustrialBPP(Balance):
    total_liabilities: decimal.Decimal
    """'Passivo Total'
    
    Note: this includes `net_equity`. Don't blame me, I only wrote the code.
    """

    current_liabilities: decimal.Decimal
    social_and_labor_obligations: decimal.Decimal
    suppliers: decimal.Decimal
    current_tax_liabilities: decimal.Decimal
    current_loans_and_financing: decimal.Decimal
    other_current_liabilities: decimal.Decimal
    current_provisions: decimal.Decimal
    current_liabilities_on_noncurrent_assets: decimal.Decimal
    noncurrent_liabilities: decimal.Decimal
    noncurrent_loans_and_financing: decimal.Decimal
    other_noncurrent_liabilities: decimal.Decimal
    deferred_tax_liabilities: decimal.Decimal
    noncurrent_provisions: decimal.Decimal
    noncurrent_liabilities_on_noncurrent_assets: decimal.Decimal
    deferred_profit_and_revenue: decimal.Decimal
    net_equity: decimal.Decimal

    __individual_layout__ = (
        ('2',        'Passivo Total',                                                'total_liabilities'),
        ('2.01',     'Passivo Circulante',                                           'current_liabilities'),
        ('2.01.01',  'Obrigações Sociais e Trabalhistas',                            'social_and_labor_obligations'),
        ('2.01.02',  'Fornecedores',                                                 'suppliers'),
        ('2.01.03',  'Obrigações Fiscais',                                           'current_tax_liabilities'),
        ('2.01.04',  'Empréstimos e Financiamentos',                                 'current_loans_and_financing'),
        ('2.01.05',  'Outras Obrigações',                                            'other_current_liabilities'),
        ('2.01.06',  'Provisões',                                                    'current_provisions'),
        ('2.01.07',  'Passivos sobre Ativos Não-Correntes a Venda e Descontinuados', 'current_liabilities_on_noncurrent_assets'),
        ('2.02',     'Passivo Não Circulante',                                       'noncurrent_liabilities'),
        ('2.02.01',  'Empréstimos e Financiamentos',                                 'noncurrent_loans_and_financing'),
        ('2.02.02',  'Outras Obrigações',                                            'other_noncurrent_liabilities'),
        ('2.02.03',  'Tributos Diferidos',                                           'deferred_tax_liabilities'),
        ('2.02.04',  'Provisões',                                                    'noncurrent_provisions'),
        ('2.02.05',  'Passivos sobre Ativos Não-Correntes a Venda e Descontinuados', 'noncurrent_liabilities_on_noncurrent_assets'),

        # https://www.ehow.com.br/considerado-receita-apropriar-info_340699/
        # https://greedhead.net/what-is-a-liability-arising-when-a-customer-pays-in-advance-of-receiving-service/
        ('2.02.06',  'Lucros e Receitas a Apropriar',                                'deferred_profit_and_revenue'),

        ('2.03',     'Patrimônio Líquido',                                           'net_equity'),
        # ('2.03.01',  'Capital Social Realizado',                                     '_'),
        # ('2.03.02',  'Reservas de Capital',                                          '_'),
        # ('2.03.03',  'Reservas de Reavaliação',                                      '_'),
        # ('2.03.04',  'Reservas de Lucros',                                           '_'),
        # ('2.03.05',  'Lucros/Prejuízos Acumulados',                                  '_'),
        # ('2.03.06',  'Ajustes de Avaliação Patrimonial',                             '_'),
        # ('2.03.07',  'Ajustes Acumulados de Conversão',                              '_'),
        # ('2.03.08',  'Outros Resultados Abrangentes',                                '_'),
        # ('2.03.09',  'Participação dos Acionistas Não Controladores',                '_'),
    )

    __consolidated_layout__ = (
        ('2',        'Passivo Total',                                                'total_liabilities'),
        ('2.01',     'Passivo Circulante',                                           'current_liabilities'),
        ('2.01.01',  'Obrigações Sociais e Trabalhistas',                            'social_and_labor_obligations'),
        ('2.01.02',  'Fornecedores',                                                 'suppliers'),
        ('2.01.03',  'Obrigações Fiscais',                                           'current_tax_liabilities'),
        ('2.01.04',  'Empréstimos e Financiamentos',                                 'current_loans_and_financing'),
        ('2.01.05',  'Outras Obrigações',                                            'other_current_liabilities'),
        ('2.01.06',  'Provisões',                                                    'current_provisions'),
        ('2.01.07',  'Passivos sobre Ativos Não-Correntes a Venda e Descontinuados', 'current_liabilities_on_noncurrent_assets'),
        ('2.02',     'Passivo Não Circulante',                                       'noncurrent_liabilities'),
        ('2.02.01',  'Empréstimos e Financiamentos',                                 'noncurrent_loans_and_financing'),
        ('2.02.02',  'Outras Obrigações',                                            'other_noncurrent_liabilities'),
        ('2.02.03',  'Tributos Diferidos',                                           'deferred_tax_liabilities'),
        ('2.02.04',  'Provisões',                                                    'noncurrent_provisions'),
        ('2.02.05',  'Passivos sobre Ativos Não-Correntes a Venda e Descontinuados', 'noncurrent_liabilities_on_noncurrent_assets'),
        ('2.02.06',  'Lucros e Receitas a Apropriar',                                'deferred_profit_and_revenue'),
        ('2.03',     'Patrimônio Líquido Consolidado',                               'net_equity'),
        # ('2.03.01',  'Capital Social Realizado',                                     '_'),
        # ('2.03.02',  'Reservas de Capital',                                          '_'),
        # ('2.03.03',  'Reservas de Reavaliação',                                      '_'),
        # ('2.03.04',  'Reservas de Lucros',                                           '_'),
        # ('2.03.05',  'Lucros/Prejuízos Acumulados',                                  '_'),
        # ('2.03.06',  'Ajustes de Avaliação Patrimonial',                             '_'),
        # ('2.03.07',  'Ajustes Acumulados de Conversão',                              '_'),
        # ('2.03.08',  'Outros Resultados Abrangentes',                                '_'),
        # ('2.03.09',  'Participação dos Acionistas Não Controladores',                '_'),
    )

    __slots__ = [
        'total_liabilities',
        'current_liabilities',
        'social_and_labor_obligations',
        'suppliers',
        'current_tax_liabilities',
        'current_loans_and_financing',
        'other_current_liabilities',
        'current_provisions',
        'current_liabilities_on_noncurrent_assets',
        'noncurrent_liabilities',
        'noncurrent_loans_and_financing',
        'other_noncurrent_liabilities',
        'deferred_tax_liabilities',
        'noncurrent_provisions',
        'noncurrent_liabilities_on_noncurrent_assets',
        'deferred_profit_and_revenue',
        'net_equity'
    ]