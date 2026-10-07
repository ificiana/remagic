"""The immutable :class:`Pattern` type and its combinators."""

from __future__ import annotations

import importlib
import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Literal

from .exceptions import RemagicException

Engine = Literal["auto", "re", "regex"]

_FLAGS = frozenset("aiLmsux")
_SCOPED_OFF = frozenset("imsx")
_ENCODINGS = frozenset("aLu")
_CLASS_SPECIALS = re.compile(r"([\\\]\[^\-&~|])")


class Precedence(IntEnum):
    """Binding strength of a pattern, used to decide when to add `(?:...)`."""

    ALTERNATION = 0
    SEQUENCE = 1
    QUANTIFIED = 2
    ATOM = 3


def _check_count(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected int, got {type(value).__name__}")
    if value < 0:
        raise RemagicException("repeat counts must not be negative")
    return value


def _check_name(name: str) -> str:
    if not (isinstance(name, str) and name.isidentifier() and name.isascii()):
        raise RemagicException(f"invalid group name: {name!r}")
    return name


def class_escape(text: str) -> str:
    """Escape characters that are special inside a `[...]` class."""
    return _CLASS_SPECIALS.sub(r"\\\1", text)


@dataclass(frozen=True, slots=True)
class Pattern:
    """An immutable piece of regular expression.

    Strings combined with a pattern are matched literally. Combining patterns
    adds `(?:...)` only where precedence requires it.

    >>> (Pattern.literal("a") | "b").times(2).source
    '(?:a|b){2}'
    """

    source: str = ""
    precedence: Precedence = Precedence.SEQUENCE
    needs_regex: bool = False

    @classmethod
    def literal(cls, text: str) -> Pattern:
        """Match `text` exactly, escaping every special character."""
        if not isinstance(text, str):
            raise TypeError(f"expected str, got {type(text).__name__}")
        precedence = Precedence.ATOM if len(text) == 1 else Precedence.SEQUENCE
        return cls(re.escape(text), precedence)

    @classmethod
    def raw(cls, source: str, *, needs_regex: bool = False) -> Pattern:
        """Wrap an existing regex source, treated as lowest precedence."""
        return cls(source, Precedence.ALTERNATION, needs_regex)

    @classmethod
    def coerce(cls, value: Pattern | str) -> Pattern:
        """Return `value` as a pattern; strings become literals."""
        if isinstance(value, Pattern):
            return value
        return cls.literal(value)

    def _as(self, minimum: Precedence) -> str:
        if self.precedence >= minimum:
            return self.source
        return f"(?:{self.source})"

    def _wrap(self, source: str, precedence: Precedence = Precedence.ATOM) -> Pattern:
        return Pattern(source, precedence, self.needs_regex)

    def __str__(self) -> str:
        return self.source

    def __add__(self, other: Pattern | str) -> Pattern:
        """Concatenate: `a + b` matches `a` then `b`."""
        if not isinstance(other, Pattern | str):
            return NotImplemented
        right = Pattern.coerce(other)
        if not self.source:
            return right
        if not right.source:
            return self
        return Pattern(
            self._as(Precedence.SEQUENCE) + right._as(Precedence.SEQUENCE),
            Precedence.SEQUENCE,
            self.needs_regex or right.needs_regex,
        )

    def __radd__(self, other: str) -> Pattern:
        if not isinstance(other, str):
            return NotImplemented
        return Pattern.literal(other) + self

    def __or__(self, other: Pattern | str) -> Pattern:
        """Alternate: `a | b` matches `a` or `b`."""
        if not isinstance(other, Pattern | str):
            return NotImplemented
        right = Pattern.coerce(other)
        return Pattern(
            f"{self.source}|{right.source}",
            Precedence.ALTERNATION,
            self.needs_regex or right.needs_regex,
        )

    def __ror__(self, other: str) -> Pattern:
        if not isinstance(other, str):
            return NotImplemented
        return Pattern.literal(other) | self

    def __mul__(self, count: int) -> Pattern:
        """`a * 3` is `a.times(3)`."""
        if not isinstance(count, int):
            return NotImplemented
        return self.times(count)

    def _quantify(self, suffix: str, lazy: bool, possessive: bool) -> Pattern:
        if lazy and possessive:
            raise RemagicException("a quantifier cannot be both lazy and possessive")
        if lazy:
            suffix += "?"
        elif possessive:
            suffix += "+"
        return self._wrap(self._as(Precedence.ATOM) + suffix, Precedence.QUANTIFIED)

    def times(
        self, count: int, *, lazy: bool = False, possessive: bool = False
    ) -> Pattern:
        """Repeat exactly `count` times."""
        return self.between(count, count, lazy=lazy, possessive=possessive)

    def between(
        self, low: int, high: int, *, lazy: bool = False, possessive: bool = False
    ) -> Pattern:
        """Repeat from `low` to `high` times, inclusive."""
        _check_count(low)
        _check_count(high)
        if low > high:
            raise RemagicException("the upper bound is below the lower bound")
        if (low, high) == (0, 1):
            suffix = "?"
        elif low == high:
            suffix = f"{{{low}}}"
        else:
            suffix = f"{{{low},{high}}}"
        return self._quantify(suffix, lazy, possessive)

    def at_least(
        self, low: int, *, lazy: bool = False, possessive: bool = False
    ) -> Pattern:
        """Repeat `low` or more times."""
        _check_count(low)
        suffix = {0: "*", 1: "+"}.get(low, f"{{{low},}}")
        return self._quantify(suffix, lazy, possessive)

    def optional(self, *, lazy: bool = False, possessive: bool = False) -> Pattern:
        """Match zero or one time."""
        return self.between(0, 1, lazy=lazy, possessive=possessive)

    def zero_or_more(self, *, lazy: bool = False, possessive: bool = False) -> Pattern:
        """Match zero or more times."""
        return self.at_least(0, lazy=lazy, possessive=possessive)

    def one_or_more(self, *, lazy: bool = False, possessive: bool = False) -> Pattern:
        """Match one or more times."""
        return self.at_least(1, lazy=lazy, possessive=possessive)

    def group(self, name: str | None = None) -> Pattern:
        """Capture as a numbered group, or as a named group if `name` is given."""
        if name is None:
            return self._wrap(f"({self.source})")
        return self._wrap(f"(?P<{_check_name(name)}>{self.source})")

    def non_capturing(self) -> Pattern:
        """Group without capturing."""
        return self._wrap(f"(?:{self.source})")

    def atomic(self) -> Pattern:
        """Match without backtracking into the group."""
        return self._wrap(f"(?>{self.source})")

    def scoped(self, on: str = "", off: str = "") -> Pattern:
        """Apply inline flags to this pattern only.

        `on` and `off` are flag letters as in `(?i-s:...)`.
        """
        if not on and not off:
            raise RemagicException("scoped needs at least one flag")
        if not (set(on) | set(off)) <= _FLAGS:
            raise RemagicException(f"unknown flags in {on + off!r}")
        if set(on) & set(off):
            raise RemagicException("a flag cannot be both on and off")
        if not set(off) <= _SCOPED_OFF:
            raise RemagicException("only i, m, s and x can be turned off")
        if len(set(on) & _ENCODINGS) > 1:
            raise RemagicException("a, L and u are mutually exclusive")
        minus = f"-{off}" if off else ""
        return self._wrap(f"(?{on}{minus}:{self.source})")

    def ignore_case(self) -> Pattern:
        """Match case-insensitively."""
        return self.scoped("i")

    def multiline(self) -> Pattern:
        """Make `^` and `$` match at line boundaries."""
        return self.scoped("m")

    def dotall(self) -> Pattern:
        """Make `.` match newlines."""
        return self.scoped("s")

    def lookahead(self) -> Pattern:
        """Assert that this pattern follows, without consuming it."""
        return self._wrap(f"(?={self.source})", Precedence.QUANTIFIED)

    def negative_lookahead(self) -> Pattern:
        """Assert that this pattern does not follow."""
        return self._wrap(f"(?!{self.source})", Precedence.QUANTIFIED)

    def lookbehind(self) -> Pattern:
        """Assert that this pattern precedes."""
        return self._wrap(f"(?<={self.source})", Precedence.QUANTIFIED)

    def negative_lookbehind(self) -> Pattern:
        """Assert that this pattern does not precede."""
        return self._wrap(f"(?<!{self.source})", Precedence.QUANTIFIED)

    def followed_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` follows."""
        return self + Pattern.coerce(other).lookahead()

    def not_followed_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` does not follow."""
        return self + Pattern.coerce(other).negative_lookahead()

    def preceded_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` precedes."""
        return Pattern.coerce(other).lookbehind() + self

    def not_preceded_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` does not precede."""
        return Pattern.coerce(other).negative_lookbehind() + self

    def compile(self, flags: int = 0, *, engine: Engine = "auto") -> re.Pattern[str]:
        """Compile with `re`, or with `regex` when the pattern needs it.

        Raises:
            RemagicException: if the chosen engine cannot compile the pattern.
        """
        if engine not in ("auto", "re", "regex"):
            raise RemagicException(f"unknown engine: {engine!r}")
        if engine == "re" and self.needs_regex:
            raise RemagicException("this pattern needs the `regex` engine")
        use_regex = engine == "regex" or (engine == "auto" and self.needs_regex)
        module: Any = re
        if use_regex:
            try:
                module = importlib.import_module("regex")
            except ImportError as error:
                raise RemagicException(
                    "install remagic[regex] to use the `regex` engine"
                ) from error
        compiled: re.Pattern[str] = module.compile(self.source, flags)
        return compiled
