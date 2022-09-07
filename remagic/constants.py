from enum import Enum
from typing import Union


class Consts(Enum):
    CHAR = r"."
    WHITESPACE = r"\s"
    NOT_WHITESPACE = r"\S"
    WS = r"\s"
    NOT_WS = r"\S"
    WORD = r"\w"
    NOT_WORD = r"\W"
    DIGIT = r"\d"
    NOT_DIGIT = r"\D"
    LETTER = r"[a-zA-Z]"
    NOT_LETTER = r"[^a-zA-Z]"
    TAB = r"\t"
    NEWLINE = r"\n"
    NOT_NEWLINE = r"\N"
    N = r"\n"
    NOT_N = r"\N"
    CARRIAGE_RETURN = r"\r"
    R = r"\r"

    def __add__(self, other: Union["Consts", str]):
        if isinstance(other, Consts):
            return self.value + other.value
        return self.value + str(other)

    def __mul__(self, other: int):
        return self.value + f"{{{int(other)}}}"
