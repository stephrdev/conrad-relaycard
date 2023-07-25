from enum import EnumMeta, IntEnum
from typing import Any


# py3.12 will do this. So, <py3.12 needs own implementation of __contains__
class MetaEnum(EnumMeta):
    def __contains__(cls, item: Any) -> bool:  # noqa N805 can be called from class context so cls is good
        try:
            cls(item)
        except ValueError:
            return False
        return True


class IntEnumBase(IntEnum, metaclass=MetaEnum):
    pass


class CommandCodes(IntEnumBase):
    NOOP = 0
    SETUP = 1
    GETPORT = 2
    SETPORT = 3
    GETOPTION = 4
    SETOPTION = 5
    SETSINGLE = 6
    DELSINGLE = 7
    TOGGLE = 8


class ResponseCodes(IntEnumBase):
    NOOP = 255
    SETUP = 254
    GETPORT = 253
    SETPORT = 252
    GETOPTION = 251
    SETOPTION = 250
    SETSINGLE = 249
    DELSINGLE = 248
    TOGGLE = 247
