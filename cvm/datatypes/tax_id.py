import typing

class InvalidTaxID(ValueError):
    def __init__(self, cls, value, err_desc):
        err_msg = f"invalid value '{value}' for TaxID class {cls}: {err_desc}"

        super().__init__(err_msg)

class TaxID(int):
    __lengths__    = ()
    __separators__ = ''

    @classmethod
    def digit_count(cls) -> int:
        return sum(cls.__lengths__)

    @classmethod
    def from_string(cls, value: str) -> str:
        lengths    = cls.__lengths__
        separators = cls.__separators__ + '\0'
        index      = 0
        digits     = ''

        value += '\0'

        for length, sep in zip(lengths, separators):            
            for j in range(index, index + length):
                try:
                    c = value[j]
                except IndexError:
                    raise InvalidTaxID(cls, value, f"expected digit character at index {j}, which is out of range") from None

                if not c.isdigit():
                    raise InvalidTaxID(cls, value, f"expected digit character at index {j} (got: '{c}')")

                digits += c

            index += length

            try:
                c = value[index]
            except IndexError:
                raise InvalidTaxID(cls, value, f"expected character '{sep}' at index {index}, which is out of range") from None
            
            if c != sep:
                raise InvalidTaxID(cls, value, f"expected character '{sep}' at index {index} (got: '{c}')")
            
            index += 1 # skip separator

        return digits

    def __new__(cls, value: typing.Union[str, int]):
        if isinstance(value, str):
            if not value.isdigit():
                value = cls.from_string(value)
                #value = ''.join(c for c in value if c.isdigit())

        return super(TaxID, cls).__new__(cls, value)

    def __str__(self) -> str:
        # Make formatter string (e.g. '{:011}' or '{:013}')
        formatter = f'{{:0{self.digit_count()}}}'

        # Make tax id zero-padded (e.g. '00000000123' (CPF) or '00000000000123' (CNPJ))
        tax_id             = int(self)
        zero_padded_tax_id = formatter.format(tax_id)

        # Format zero-padded value (e.g. '123.456.789-00' (CPF) or '12.345.678.9999-00' (CNPJ))
        lengths    = self.__lengths__
        separators = self.__separators__ + '\0'
        start      = 0
        tax_id     = ''

        for length, sep in zip(lengths, separators):
            stop    = start + length
            part    = zero_padded_tax_id[start:stop]
            tax_id += part + sep
            start   = stop

        return tax_id[:-1]

class CNPJ(TaxID):
    __lengths__    = (2, 3, 3, 4, 2)
    __separators__ = '../-'

    def __repr__(self) -> str:
        return f'<CNPJ: { self.__str__() }>'

class CPF(TaxID):
    __lengths__    = (3, 3, 3, 2)
    __separators__ = '..-'

    def __repr__(self) -> str:
        return f'<CPF: { self.__str__() }>'