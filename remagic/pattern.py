"""
This module contains all the logic for working with Patterns.
"""

from functools import partial
from typing import Iterable

import regex

from .utils import class_escape

# all supported types, edit these lists before implementing new types
_supported_standalone_types = [
    "char", "digit", "ws", "whitespace", "letter",
    "tab", "linefeed", "n", "carriage_return", "r",
]
_supported_types_for_iterables = [
    "char_in", "char_not_in", "any_of", "exactly",
]
_supported_types = (_supported_types_for_iterables
                    + _supported_types_for_iterables)


class Pattern:
    """
    Class for Remagic Patterns
    """

    # True if the pattern is optional
    _maybe = False
    # True if the pattern is quantified one or more times
    _one_or_more = False

    def __init__(self, type_=None, iterable=None):
        if type_ is None:
            self.regex = ""
        elif iterable is None:
            self.regex = (
                "." if type_ == "char"
                else r"\w" if type_ == "word"
                else r"\d" if type_ == "digit"
                else r"\s" if type_ in ("whitespace", "ws")
                else "[a-zA-Z]" if type_ == "letter"
                else r"\t" if type_ == "tab"
                else r"\n" if type_ in ("linefeed", "n")
                else r"\r" if type_ in ("carriage_return", "r")
                else None
            )
        elif isinstance(iterable, Iterable):
            if type_ == "exactly":
                self.regex = f"{iterable}"
            else:
                self.it_ = class_escape(iterable)
                self.regex = (
                    rf"[{self.it_}]" if type_ == "char_in"
                    else rf"[^{self.it_}]" if type_ == "char_not_in"
                    else self.any(iterable) if type_ == "any_of"
                    else None
                )
        if self.regex is None:
            raise ValueError(f"Type `{type_}` is not appropriate")
        self.type = type_

    @staticmethod
    def any(iterable):
        """
        Make alternatives for matching
        Usage:
            >>> import remagic
            >>> pattern = remagic.create(remagic.any_of())
            >>> print(pattern)
            <remagic.Pattern object; pattern=r"\\d">
            >>> print(~pattern)
            <remagic.Pattern object; pattern=r"\\D">
            >>> print(pattern.not_)
        :param iterable: An Iterable with string values or a string
        :return:
        """
        res = exactly("(")
        for i in iterable:
            res += exactly("|") + i
        res += ")"
        try:
            return regex.sub(r"^\(\|", "(", res)
        except TypeError:
            return regex.sub(r"^\(\|", "(", res.regex)

    @property
    def not_(self):
        """
        Negates the Pattern, alias for inversion operator
        Usage:
            >>> import remagic
            >>> pattern = remagic.create(remagic.DIGIT)
            >>> print(pattern)
            <remagic.Pattern object; pattern=r"\\d">
            >>> print(~pattern)
            <remagic.Pattern object; pattern=r"\\D">
            >>> print(pattern.not_)
            <remagic.Pattern object; pattern=r"\\D">
        :return: negated Pattern object
        """
        return self.__invert__()

    @property
    def maybe(self):
        if self._maybe:
            return exactly(regex.compile(r"\((.+)\)\+").sub(r"\g<1>",
                                                            self.regex))
        self._maybe ^= True
        return -self

    @property
    def one_or_more(self):
        if self._one_or_more:
            return exactly(regex.compile(r"\((.+)\)\?").sub(r"\g<1>",
                                                            self.regex))
        self._one_or_more ^= True
        return +self

    def add(self, other):
        return self + other

    def multipy(self, num: int):
        return self * num

    def compile(self, *args, **kwargs):
        return regex.compile(self.regex, *args, **kwargs)

    def __add__(self, other):
        if isinstance(other, Pattern):
            return exactly(self.regex + other.regex)
        if isinstance(other, str):
            return exactly(self.regex + regex.escape(other))
        raise TypeError(f"Unsupported Type: {type(other)}")

    def __invert__(self):
        res = (
            r"\W" if self.type == "word"
            else r"\D" if self.type == "digit"
            else r"\S" if self.type in ("whitespace", "ws")
            else "[^a-zA-Z]" if self.type == "letter"
            else r"[^\t]" if self.type == "tab"
            else r"[^\n]" if self.type in ("linefeed", "n")
            else r"[^\r]" if self.type in ("carriage_return", "r")
            else ""
        )
        return exactly(res)

    def __iter__(self):
        return iter(self.regex)

    def __pos__(self):
        res = f"({self.regex})+"
        return exactly(res)

    def __neg__(self):
        res = f"({self.regex})?"
        return exactly(res)

    def __mul__(self, other):
        if isinstance(other, int) and other >= 0:
            return exactly(f"({self.regex}){{{other}}}")
        raise ValueError("Invalid value provided")

    def __repr__(self):
        return f"<remagic.Pattern object; pattern=r\"{self.regex}\">"


class PatternIterable(Pattern):
    def __init__(self, type_, iterable):
        super().__init__(type_, iterable)


exactly = partial(PatternIterable, "exactly", )
empty = Pattern()
types = {i.upper(): Pattern(i) for i in _supported_standalone_types}
types.update({i: partial(Pattern, i) for i in _supported_types_for_iterables})
