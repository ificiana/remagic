"""Ready-made patterns for common character classes and anchors."""

from __future__ import annotations

from .pattern import Pattern, Precedence


def _atom(source: str) -> Pattern:
    return Pattern(source, Precedence.ATOM)


def _assertion(source: str) -> Pattern:
    return Pattern(source, Precedence.QUANTIFIED)


#: Any character except a newline.
CHAR = _atom(".")
#: One whitespace character; also available as `WS`.
WHITESPACE = WS = _atom(r"\s")
#: One non-whitespace character; also available as `NOT_WS`.
NOT_WHITESPACE = NOT_WS = _atom(r"\S")
#: One word character (letter, digit or underscore).
WORD = _atom(r"\w")
#: One non-word character.
NOT_WORD = _atom(r"\W")
#: One decimal digit.
DIGIT = _atom(r"\d")
#: One character that is not a digit.
NOT_DIGIT = _atom(r"\D")
#: One ASCII letter.
LETTER = _atom("[a-zA-Z]")
#: One character that is not an ASCII letter.
NOT_LETTER = _atom("[^a-zA-Z]")
#: A tab.
TAB = _atom(r"\t")
#: A newline; also available as `N`.
NEWLINE = N = _atom(r"\n")
#: Any character except a newline; also available as `NOT_N`.
NOT_NEWLINE = NOT_N = _atom(r"[^\n]")
#: A carriage return; also available as `R`.
CARRIAGE_RETURN = R = _atom(r"\r")

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
