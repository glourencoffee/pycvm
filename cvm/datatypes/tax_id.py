from __future__ import annotations

__all__ = [
    'InvalidTaxID',
    'TaxID',
    'CNPJ',
    'CPF'
]

class InvalidTaxID(ValueError):
    def __init__(self, cls, value, err_desc):
        err_msg = f"invalid value '{value}' for TaxID class {cls}: {err_desc}"

        super().__init__(err_msg)

class TaxID:
    """
    There are three ways of representing a tax id:
    1. plain digits (e.g. "191");
    2. zero-filled digits (e.g. "00000000000191");
    3. zero-filled digits with separators (e.g. "00.000.000/0001-91").

    Subclasses of this class only accept representations 1 and 2 upon
    construction:

    >>> CNPJ('191')
    '00000000000191'
    >>> CNPJ('00000000000191')
    '00000000000191'

    Passing a string with non-digit characters raises `InvalidTaxID`.
    To construct a `TaxID` from representation 3, call the class method
    `from_zfilled_with_separators()`:

    >>> cnpj = CNPJ.from_zfilled_with_separators('00.000.000/0001-91')
    >>> str(cnpj)
    '00000000000191'
    >>> cnpj.digits()
    '191'
    """

    _lengths    = ()
    _separators = ''

    __slots__ = '_digits'

    @classmethod
    def digit_count(cls) -> int:
        return sum(cls._lengths)

    @classmethod
    def from_zfilled_with_separators(cls, value: str) -> TaxID:
        lengths    = cls._lengths
        separators = cls._separators + '\0'
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
        
        return cls(digits)

    def __init__(self, digits: str) -> str:
        digits = digits.lstrip('0')

        if len(digits) == 0:
            raise InvalidTaxID(self.__class__, digits, 'tax id digits must not be empty or zero')

        for c in digits:
            if not c.isdigit():
                raise InvalidTaxID(
                    self.__class__,
                    digits,
                    f"tax id must contain only digits (got '{c}')"
                )

        if len(digits) > self.digit_count():
            raise InvalidTaxID(
                self.__class__,
                digits,
                f"tax id is too large (max digits: {self.digit_count()}, got: {len(digits)})"
            )

        self._digits = digits

    def digits(self) -> str:
        return self._digits

    def to_string(self, use_separator: bool = True) -> str:
        # Make tax id zero-padded (e.g. '00000000123' (CPF) or '00000000000123' (CNPJ))
        zero_padded_digits = self._digits.zfill(self.digit_count())

        if use_separator:
            # Format zero-padded value (e.g. '123.456.789-00' (CPF) or '12.345.678/9999-00' (CNPJ))
            lengths    = self._lengths
            separators = self._separators + '\0'
            start      = 0
            new_digits = ''

            for length, sep in zip(lengths, separators):
                stop        = start + length
                part        = zero_padded_digits[start:stop]
                new_digits += part + sep
                start       = stop

            zero_padded_digits = new_digits[:-1]

        return zero_padded_digits

    def __str__(self) -> str:
        return self.to_string(use_separator=True)

    # def __eq__(self, other: object) -> bool:
    #     return self.digits() == other.digits()

    # def __ne__(self, other: object) -> bool:
    #     return not self.__eq__(other)

class CNPJ(TaxID):
    _lengths    = (2, 3, 3, 4, 2)
    _separators = '../-'

    def __repr__(self) -> str:
        return f'<CNPJ: {self.to_string(use_separator=True)}>'

class CPF(TaxID):
    _lengths    = (3, 3, 3, 2)
    _separators = '..-'

    def __repr__(self) -> str:
        return f'<CPF: {self.to_string(use_separator=True)}>'