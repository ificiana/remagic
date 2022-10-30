"""
Implements RegEx abstraction logic, for easy working with RegEx in Python.
"""
import sys

from .interface import (
    after,
    any_of,
    before,
    char_in,
    char_not_in,
    create,
    exactly,
    not_after,
    not_before,
    one_or_more,
    optional,
    ref,
    zero_or_more,
)

if sys.version_info >= (3, 8):  # pragma: no cover
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata  # pragma: no cover


def _metadata():
    return importlib_metadata.metadata(__name__)


__metadata__ = _metadata()


def get_version() -> str:
    try:
        return str(__metadata__["version"])
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

__title__ = __metadata__["name"]
__version__ = version
__author__ = __metadata__["author"]
__license__ = __metadata__["licence"]
__copyright__ = "Copyright 2022 Ificiana"

CHAR = create(r".")
WHITESPACE = WS = create(r"\s")
NOT_WHITESPACE = NOT_WS = create(r"\S")
WORD = create(r"\w")
NOT_WORD = create(r"\W")
DIGIT = create(r"\d")
NOT_DIGIT = create(r"\D")
LETTER = create(r"[a-zA-Z]")
NOT_LETTER = create(r"[^a-zA-Z]")
TAB = create(r"\t")
NEWLINE = N = create(r"\n")
NOT_NEWLINE = NOT_N = create(r"\N")
CARRIAGE_RETURN = R = create(r"\r")

__all__ = [
    "CARRIAGE_RETURN",
    "CHAR",
    "DIGIT",
    "LETTER",
    "N",
    "NEWLINE",
    "NOT_DIGIT",
    "NOT_LETTER",
    "NOT_N",
    "NOT_NEWLINE",
    "NOT_WHITESPACE",
    "NOT_WORD",
    "NOT_WS",
    "R",
    "TAB",
    "WHITESPACE",
    "WORD",
    "WS",
    "after",
    "any_of",
    "before",
    "char_in",
    "char_not_in",
    "create",
    "exactly",
    "not_after",
    "not_before",
    "one_or_more",
    "optional",
    "version",
    "get_version",
    "zero_or_more",
    "ref",
]
