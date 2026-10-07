"""Ready-made patterns for common character classes and anchors."""

from __future__ import annotations

from . import _tree as tree
from .pattern import Pattern


def _esc(token: str) -> Pattern:
    return Pattern(tree.Esc(token))


def _lit(char: str) -> Pattern:
    return Pattern(tree.Lit(char))


def _set(*ranges: tuple[str, str], negate: bool = False) -> Pattern:
    spans = [(ord(low), ord(high)) for low, high in ranges]
    return Pattern(tree.make_charset((), spans, negate))


def _assertion(token: str) -> Pattern:
    return Pattern(tree.Assertion(token))


#: Any character except a newline.
CHAR = _esc(".")
#: One whitespace character; also available as `WS`.
WHITESPACE = WS = _esc(r"\s")
#: One non-whitespace character; also available as `NOT_WS`.
NOT_WHITESPACE = NOT_WS = _esc(r"\S")
#: One word character (letter, digit or underscore).
WORD = _esc(r"\w")
#: One non-word character.
NOT_WORD = _esc(r"\W")
#: One decimal digit.
DIGIT = _esc(r"\d")
#: One character that is not a digit.
NOT_DIGIT = _esc(r"\D")
#: One ASCII letter.
LETTER = _set(("a", "z"), ("A", "Z"))
#: One character that is not an ASCII letter.
NOT_LETTER = _set(("a", "z"), ("A", "Z"), negate=True)
#: A tab.
TAB = _lit("\t")
#: A newline; also available as `N`.
NEWLINE = N = _lit("\n")
#: Any character except a newline; also available as `NOT_N`.
NOT_NEWLINE = NOT_N = _set(("\n", "\n"), negate=True)
#: A carriage return; also available as `R`.
CARRIAGE_RETURN = R = _lit("\r")

#: The start of the string, or of a line when multiline.
START = _assertion("^")
#: The end of the string, or of a line when multiline.
END = _assertion("$")
#: The very start of the string.
START_OF_STRING = _assertion(r"\A")
#: The very end of the string.
END_OF_STRING = _assertion(r"\Z")
#: The boundary between a word and a non-word character.
WORD_BOUNDARY = _assertion(r"\b")
#: Any position that is not a word boundary.
NOT_WORD_BOUNDARY = _assertion(r"\B")
