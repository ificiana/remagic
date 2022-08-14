from enum import Enum
from typing import Union


class Consts(Enum):
    CHAR = r"."
    WHITESPACE = r"\s"
    WS = r"\s"
    WORD = r"\w"
    DIGIT = r"\d"
    LETTER = r"[a-zA-Z]"
    TAB = r"\t"
    LINEFEED = r"\n"
    N = r"\n"
    CARRIAGE_RETURN = r"\r"
    R = r"\r"

    def __add__(self, other: Union["Consts", str]):
        if isinstance(other, Consts):
            return self.value + other.value
        return self.value + str(other)

    def __mul__(self, other: int):
        return self.value + f"{{{int(other)}}}"
