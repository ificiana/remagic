import warnings
from typing import Union

from .constants import Consts

try:
    import regex as re  # type: ignore
except ImportError:
    import re  # type: ignore

    warnings.warn("`regex` module not found, using builtin `re` module", ImportWarning)


class Pattern:
    _pattern: str

    def __init__(self, pattern=""):
        self._pattern = pattern

    def create(self, const: Consts) -> "Pattern":
        self._pattern = const.value
        return self

    def compile(self) -> "re.Pattern":
        return re.compile(self._pattern)

    def add(self, other: Union[str, "Pattern"]):
        """
        Function to add two Patterns
        :param other: Pattern
        :return: other Pattern appended to this Pattern
        """
        return self + other

    def mul(self, num: int) -> "Pattern":
        return self * num

    @property
    def pattern(self) -> str:
        return self._pattern

    @pattern.getter
    def pattern(self) -> str:
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        self._pattern = value

    def __add__(self, other: Union["Pattern", str]) -> "Pattern":
        if isinstance(other, Pattern):
            return Pattern(self._pattern + other._pattern)
        return Pattern(self._pattern + str(other))

    def __mul__(self, num: int) -> "Pattern":
        return Pattern(self._pattern + f"{{{int(num)}}}")

    def __str__(self) -> str:
        return self._pattern
