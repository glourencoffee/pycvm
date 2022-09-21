import functools
import typing

__all__ = [
    'cvm_codes'
]

@functools.lru_cache
def _cvm_codes() -> typing.List[str]:
    return [
        '1023',  # BCO BRASIL S.A.
        '1120',  # BCO ESTADO DE SERGIPE S.A. - BANESE
        '1155',  # BANESTES S.A. - BCO EST ESPIRITO SANTO
        '1210',  # BCO ESTADO DO RIO GRANDE DO SUL S.A.
        '1325',  # BCO MERCANTIL DO BRASIL S.A.
        '1384',  # BCO ALFA DE INVESTIMENTO S.A.
        '14206', # BRB BCO DE BRASILIA S.A.
        '19348', # ITAU UNIBANCO HOLDING S.A.
        '20532', # BCO SANTANDER (BRASIL) S.A.
        '20567', # BCO PINE S.A.
        '20680', # BANCO SOFISA SA
        '20729', # PARANA BCO S.A.
        '20753', # BANCO CRUZEIRO DO SUL SA
        '20796', # BCO DAYCOVAL S.A.
        '20885', # BCO INDUSVAL S.A.
        '20958', # BCO ABC BRASIL S.A.
        '21113', # BANCO INDUSTRIAL E COMERCIAL S/A
        '21199', # BCO PAN S.A.
        '21377', # BANCO INDUSTRIAL DO BRASIL
        '21466', # BANCO RCI BRASIL S.A.
        '22616', # BCO BTG PACTUAL S.A.
        '22993', # COMPANHIA DE CRÉDITO FINANCIAMENTO E INVESTIMENTO RCI BRASIL
        '24600', # BANCO BMG S/A
        '80063', # BCO PATAGONIA S.A.
        '80152', # PPLA PARTICIPATIONS LTD.
        '80160', # BANCO SANTANDER S.A.
        '906',   # BCO BRADESCO S.A.
        '24406', # BANCO INTER S.A.
    ]

def cvm_codes() -> typing.List[str]:
    """
    Returns CVM codes of companies that use the
    account layout of financial institutions.
    """

    return _cvm_codes().copy()