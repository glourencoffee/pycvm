from typing import Union

class CNPJ(int):
    def __new__(cls, value: Union[str, int]):
        if isinstance(value, str):
            value = ''.join(c for c in value if c.isdigit())

        return super(cls, cls).__new__(cls, value)

    def __str__(self) -> str:
        cnpj             = int(self)
        zero_padded_cnpj = f'{cnpj:014}'

        lengths    = (2, 3, 3, 4, 2)
        separators = '../-\0'
        start      = 0
        cnpj       = ''

        for length, sep in zip(lengths, separators):
            stop  = start + length
            part  = zero_padded_cnpj[start:stop]
            cnpj += part + sep
            start = stop

        return cnpj.rstrip('\0')

    def __repr__(self) -> str:
        return f'<CNPJ: { self.__str__() }>'