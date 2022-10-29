from enum import Enum


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
