"""
Implements RegEx abstraction logic, for easy working with RegEx in Python.
"""
__title__ = "remagic"
__version__ = "0.0.8"
__author__ = "ificiana"
__license__ = "MIT License"
__copyright__ = "Copyright 2022 ificiana"


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
    "zero_or_more",
    "optional",
    "one_or_more",
]
