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

    def __mul__(
        self, num: Union[int, Tuple[int, int], Tuple[int]]  # noqa: E501
    ) -> "Pattern":
        if isinstance(num, tuple):
            first, second = num[0], num[1] if len(num) > 1 else None
            if first == 0 and second is None:
                return Pattern(self._pattern + "*")
            if first == 1 and second is None:
                return Pattern(self._pattern + "+")
            if first == 0 and second == 1:
                return Pattern(self._pattern + "?")
            if first == second:
                return Pattern(self._pattern + f"{{{int(first)}}}")
            return Pattern(self._pattern + f"{{{int(num[0])},{int(num[1])}}}")
        return Pattern(self._pattern + f"{{{int(num)}}}")

    def __eq__(self, other):
        return self._pattern == str(other)

    def __iter__(self):
        return iter(self._pattern)

    def __str__(self) -> str:
        return str(self._pattern)
