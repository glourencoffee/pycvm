import typing
import dataclasses

__all__ = [
    'Phone'
]

@dataclasses.dataclass(init=True, frozen=True)
class Phone:
    country_code: typing.Optional[int]
    area_code: int
    number: int

    def __str__(self) -> str:
        """Examples:
           - '+55 11 3957-9499'
           - '(47) 33735-0040'
           - '(11) 262-7218'
        """

        number = str(self.number)

        try:
            number = f'{number[:-4]}-{number[-4:]}'
        except IndexError:
            pass

        if self.country_code is None:
            return f'({self.area_code}) {number}'
        else:
            return f'+{self.country_code} {self.area_code} {number}'

    def __repr__(self) -> str:
        return f'<Phone: {self.__str__()}>'