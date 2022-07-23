"""
Implements RegEx abstraction logic, for easy working with RegEx in Python.
"""
__title__ = "remagic"
__version__ = "0.0.4"
__author__ = "ificiana"
__license__ = "MIT License"
__copyright__ = "Copyright 2022 ificiana"


from .pattern import Pattern, types
from .pattern import _supported_types
from .main import create

supported_types = _supported_types
CHAR = types["CHAR"]
DIGIT = types["DIGIT"]
LETTER = types["LETTER"]
TAB = types["TAB"]
WS = types["WS"]
WHITESPACE = types["WHITESPACE"]
N = types["N"]
LINEFEED = types["LINEFEED"]
R = types["R"]
CARRIAGE_RETURN = types["CARRIAGE_RETURN"]
char_in = types["char_in"]
char_not_in = types["char_not_in"]
any_of = types["any_of"]
exactly = types["exactly"]

__all__ = [
    "create",
    "Pattern",
    "supported_types",
    *types.keys(),
]
