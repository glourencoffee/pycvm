import functools
import typing

__all__ = [
    'cvm_codes'
]

@functools.lru_cache
def _cvm_codes() -> typing.List[str]:
    return [
        '23159', # BB SEGURIDADE PARTICIPAÇÕES S.A.
        '24180', # IRB - BRASIL RESSEGUROS S.A.
        '3115',  # CIA SEGUROS ALIANCA DA BAHIA
    ]

def cvm_codes() -> typing.List[str]:
    """
    Returns CVM codes of companies that use the
    account layout of insurance companies.
    """
    return _cvm_codes().copy()