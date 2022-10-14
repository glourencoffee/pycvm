import typing
from cvm.exceptions import ZipMemberError

class MemberNameList:
    def __init__(self, namelist: typing.Iterable[str]):
        prefix       = self.member_prefix()
        suffix       = self.member_suffix()
        prefix_len   = len(prefix)
        suffix_len   = len(suffix)
        attr_mapping = self.attribute_mapping()

        for name in namelist:
            try:
                middle_name = name[prefix_len:-suffix_len]
            except IndexError:
                raise ZipMemberError(name)

            try:
                attr_name = attr_mapping.pop(middle_name)
            except KeyError:
                # print("Unknown member file '", name, "'", sep='')
                pass
            else:
                setattr(self, attr_name, name)

        for middle_name in attr_mapping.keys():
            file_name = prefix + middle_name + suffix

            # TODO: specialize exception
            raise FileNotFoundError(f"Missing required Zip member file '{file_name}'")

    @classmethod
    def member_prefix(cls) -> str:
        return 'XXX_cia_aberta'

    @classmethod
    def member_suffix(cls) -> str:
        return '_YYYY.csv'

    @classmethod
    def attribute_mapping(cls) -> typing.Dict[str, str]:
        return {}