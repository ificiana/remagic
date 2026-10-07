"""Ready-made patterns for common character classes and anchors."""

from __future__ import annotations

from .pattern import Pattern, Precedence


def _atom(source: str) -> Pattern:
    return Pattern(source, Precedence.ATOM)


def _assertion(source: str) -> Pattern:
    return Pattern(source, Precedence.QUANTIFIED)


CHAR = _atom(".")
WHITESPACE = WS = _atom(r"\s")
NOT_WHITESPACE = NOT_WS = _atom(r"\S")
WORD = _atom(r"\w")
NOT_WORD = _atom(r"\W")
DIGIT = _atom(r"\d")
NOT_DIGIT = _atom(r"\D")
LETTER = _atom("[a-zA-Z]")
NOT_LETTER = _atom("[^a-zA-Z]")
TAB = _atom(r"\t")
NEWLINE = N = _atom(r"\n")
NOT_NEWLINE = NOT_N = _atom(r"[^\n]")
CARRIAGE_RETURN = R = _atom(r"\r")

START = _assertion("^")
END = _assertion("$")
START_OF_STRING = _assertion(r"\A")
END_OF_STRING = _assertion(r"\Z")
WORD_BOUNDARY = _assertion(r"\b")
NOT_WORD_BOUNDARY = _assertion(r"\B")
