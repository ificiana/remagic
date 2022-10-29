from typing import Tuple, Union

import warnings

from .constants import Consts

try:
    import regex as re
except ImportError:
    import re  # type: ignore[no-redef]

    warnings.warn("`regex` module not found, using builtin `re` module", ImportWarning)


class Pattern:
    _pattern: str

    def __init__(self, pattern=""):
        self._pattern = pattern

    def create_from_consts(self, const: Consts) -> "Pattern":
        self._pattern = const.value
        return self

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
        return self.add(Pattern(reference))

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

    def __mul__(self, num: Union[int, Tuple[int, ...]]) -> "Pattern":
        if isinstance(num, tuple):
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
                    raise ValueError("More than 2 values provided")
                first, second = num[0], num[1]
                if num[0] > num[1]:
                    raise ValueError("Second value cannot be less than the first")
                if first == 0 and second == 1:
                    temp = "?"
                elif first == second:
                    temp = f"{{{first}}}"
                else:
                    temp = f"{{{first},{second}}}"
            return Pattern(self._pattern + temp)
        return Pattern(self._pattern + f"{{{int(num)}}}")

    def __eq__(self, other):
        return self._pattern == str(other)

    def __iter__(self):
        return iter(self._pattern)

    def __str__(self) -> str:
        return str(self._pattern)
