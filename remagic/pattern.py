from typing import Tuple, Union

import warnings

from .exceptions import RemagicException

try:  # pragma: no cover
    import regex as re
except ImportError:  # pragma: no cover
    import re  # type: ignore[no-redef]

    warnings.warn("`regex` module not found, using builtin `re` module", ImportWarning)


class Pattern:
    _pattern: str

    def __init__(self, pattern=""):
        self._pattern = pattern

    def compile(self) -> "re.Pattern":
        return re.compile(str(self._pattern))

    def add(self, other: Union[str, "Pattern"]) -> "Pattern":
        """
        Function to add two Patterns
        :param other: Pattern
        :return: other Pattern appended to this Pattern
        """
        return self + other

    def repeat(self, num: Union[int, Tuple[int, int]]) -> "Pattern":
        return self * num

    def label(self, name):
        return Pattern(rf"(?P<{name}>{self._pattern})")

    def group(self):
        return Pattern(rf"({self._pattern})")

    def ref(self, reference):
        if isinstance(reference, int) and reference > 0:
            return self.add(rf"\{reference}")
        if isinstance(reference, str):
            return self.add(rf"(?P={reference})")
        raise RemagicException("Only positive integers and strings are allowed")

    @property
    def pattern(self) -> str:
        return self._pattern  # pragma: no cover

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

    def __mul__(self, num: Union[int, Tuple[int, ...]]) -> "Pattern":
        if isinstance(num, tuple):
            for i in num:
                if i < 0:
                    raise RemagicException("Value should be positive")
            if len(num) == 1:
                (num,) = num
                if num == 0:
                    temp = "*"
                elif num == 1:
                    temp = "+"
                else:
                    temp = f"{{{num},}}"
            else:
                if len(num) > 2:
                    raise RemagicException("More than 2 values provided")
                first, second = num[0], num[1]
                if num[0] > num[1]:
                    raise RemagicException("Second value cannot be less than the first")
                if first == 0 and second == 1:
                    temp = "?"
                elif first == second:
                    temp = f"{{{first}}}"
                else:
                    temp = f"{{{first},{second}}}"
            return Pattern(self._pattern + temp)
        if num < 0:
            raise RemagicException("Value should be positive")
        return Pattern(f"{self._pattern}{{{int(num)}}}")

    def __eq__(self, other):
        return self._pattern == str(other)

    def __iter__(self):
        return iter(self._pattern)  # pragma: no cover

    def __str__(self) -> str:
        return str(self._pattern)
