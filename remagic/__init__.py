from .constants import Consts
from .interface import *

CHAR = create(Consts.CHAR)
WHITESPACE = create(Consts.WHITESPACE)
WS = create(Consts.WS)
WORD = create(Consts.WORD)
DIGIT = create(Consts.DIGIT)
LETTER = create(Consts.LETTER)
TAB = create(Consts.TAB)
LINEFEED = create(Consts.LINEFEED)
CARRIAGE_RETURN = create(Consts.CARRIAGE_RETURN)
N = create(Consts.N)
R = create(Consts.R)

__all__ = [
    "create",
    "exactly",
    "Consts",
    "CHAR",
    "WORD",
    "WS",
    "WHITESPACE",
    "LETTER",
    "LINEFEED",
    "CARRIAGE_RETURN",
    "DIGIT",
    "TAB",
    "R",
    "N",
]
