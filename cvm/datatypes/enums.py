import enum

class CaseInsentiveEnum(enum.Enum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            lcvalue = value.lower()

            for elem in cls:
                if isinstance(elem.value, str) and elem.value.lower() == lcvalue:
                    return cls(elem.value)

        return super()._missing_(value)

class DescriptiveIntEnum(int, enum.Enum):
    __case_insensitive__ = True

    def __new__(cls, value: int, description: str):
        obj = int.__new__(cls, value)
        obj._value_      = value
        obj._description = description

        return obj

    @classmethod
    def _missing_(cls, value):
        if not isinstance(value, str):
            return super()._missing_(value)    
        
        if cls.__case_insensitive__:
            desc = value.lower()
        else:
            desc = value

        for elem in cls:
            if cls.__case_insensitive__:
                elem_desc = elem.description.lower()
            else:
                elem_desc = elem.description
        
            if desc == elem_desc:
                return cls(elem.value)

        return super()._missing_(value)

    @property
    def description(self) -> str:
        return self._description

    def __str__(self) -> str:
        return self.description

    def __repr__(self) -> str:
        return f"<{ self.__class__.__name__ }.{ self.name }: ({ self.value }, '{ self.description }')>"