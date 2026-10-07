"""The immutable :class:`Pattern` type and its combinators."""

from __future__ import annotations

import importlib
import re
from dataclasses import dataclass
from typing import Any, Literal

from . import _tree as tree
from ._tree import Level, Node, Precedence
from .exceptions import RemagicException

Engine = Literal["auto", "re", "regex"]

_FLAGS = frozenset("aiLmsux")
_SCOPED_OFF = frozenset("imsx")
_ENCODINGS = frozenset("aLu")


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


def _parts(node: Node, kind: type[tree.Seq] | type[tree.Alt]) -> tuple[Node, ...]:
    return node.parts if isinstance(node, kind) else (node,)


@dataclass(frozen=True, slots=True, repr=False)
class Pattern:
    """An immutable piece of regular expression.

    Strings combined with a pattern are matched literally. Combining patterns
    adds `(?:...)` only where precedence requires it.

    >>> (Pattern.literal("a") | "b").times(2).source
    '(?:a|b){2}'
    """

    node: Node = tree.EMPTY

    @property
    def source(self) -> str:
        """The regex source as built, before any optimisation."""
        return tree.render(self.node)

    @property
    def precedence(self) -> Precedence:
        """How tightly this pattern binds when combined."""
        return tree.precedence(self.node)

    @property
    def needs_regex(self) -> bool:
        """Whether only the `regex` module can compile this pattern."""
        return tree.needs_regex(self.node)

    @classmethod
    def literal(cls, text: str) -> Pattern:
        """Match `text` exactly, escaping every special character."""
        if not isinstance(text, str):
            raise TypeError(f"expected str, got {type(text).__name__}")
        return cls(tree.Lit(text) if text else tree.EMPTY)

    @classmethod
    def coerce(cls, value: Pattern | str) -> Pattern:
        """Return `value` as a pattern; strings become literals."""
        if isinstance(value, Pattern):
            return value
        return cls.literal(value)

    def __repr__(self) -> str:
        return f"Pattern({self.source!r})"

    def __str__(self) -> str:
        return self.source

    def __add__(self, other: Pattern | str) -> Pattern:
        """Concatenate: `a + b` matches `a` then `b`."""
        if not isinstance(other, Pattern | str):
            return NotImplemented
        right = Pattern.coerce(other)
        if self.node == tree.EMPTY:
            return right
        if right.node == tree.EMPTY:
            return self
        return Pattern(
            tree.Seq((*_parts(self.node, tree.Seq), *_parts(right.node, tree.Seq)))
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
            tree.Alt((*_parts(self.node, tree.Alt), *_parts(right.node, tree.Alt)))
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

    def _repeat(
        self, low: int, high: int | None, lazy: bool, possessive: bool
    ) -> Pattern:
        if lazy and possessive:
            raise RemagicException("a quantifier cannot be both lazy and possessive")
        mode: tree.Mode = "lazy" if lazy else "possessive" if possessive else "greedy"
        return Pattern(tree.Repeat(self.node, low, high, mode))

    def times(
        self, count: int, *, lazy: bool = False, possessive: bool = False
    ) -> Pattern:
        """Repeat exactly `count` times.

        Example:
            >>> str(Pattern.literal("a").times(3))
            'a{3}'
        """
        return self.between(count, count, lazy=lazy, possessive=possessive)

    def between(
        self, low: int, high: int, *, lazy: bool = False, possessive: bool = False
    ) -> Pattern:
        """Repeat from `low` to `high` times, inclusive.

        Example:
            >>> str(Pattern.literal("a").between(2, 4))
            'a{2,4}'
        """
        _check_count(low)
        _check_count(high)
        if low > high:
            raise RemagicException("the upper bound is below the lower bound")
        return self._repeat(low, high, lazy, possessive)

    def at_least(
        self, low: int, *, lazy: bool = False, possessive: bool = False
    ) -> Pattern:
        """Repeat `low` or more times.

        Example:
            >>> str(Pattern.literal("a").at_least(2))
            'a{2,}'
        """
        _check_count(low)
        return self._repeat(low, None, lazy, possessive)

    def optional(self, *, lazy: bool = False, possessive: bool = False) -> Pattern:
        """Match zero or one time.

        Example:
            >>> str(Pattern.literal("a").optional(lazy=True))
            'a??'
        """
        return self.between(0, 1, lazy=lazy, possessive=possessive)

    def zero_or_more(self, *, lazy: bool = False, possessive: bool = False) -> Pattern:
        """Match zero or more times.

        Example:
            >>> str(Pattern.literal("ab").zero_or_more())
            '(?:ab)*'
        """
        return self.at_least(0, lazy=lazy, possessive=possessive)

    def one_or_more(self, *, lazy: bool = False, possessive: bool = False) -> Pattern:
        """Match one or more times.

        Example:
            >>> str(Pattern.literal("a").one_or_more(possessive=True))
            'a++'
        """
        return self.at_least(1, lazy=lazy, possessive=possessive)

    def group(self, name: str | None = None) -> Pattern:
        """Capture as a numbered group, or as a named group if `name` is given.

        Example:
            >>> str(Pattern.literal("a").group("first"))
            '(?P<first>a)'
        """
        if name is None:
            return Pattern(tree.Group(self.node))
        return Pattern(tree.Group(self.node, _check_name(name)))

    def non_capturing(self) -> Pattern:
        """Group without capturing.

        Example:
            >>> str(Pattern.literal("ab").non_capturing())
            '(?:ab)'
        """
        return Pattern(tree.NonCapture(self.node))

    def atomic(self) -> Pattern:
        """Match without backtracking into the group.

        Example:
            >>> str(Pattern.literal("a").atomic())
            '(?>a)'
        """
        return Pattern(tree.Atomic(self.node))

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
        return Pattern(tree.Scoped(self.node, on, off))

    def ignore_case(self) -> Pattern:
        """Match case-insensitively.

        Example:
            >>> str(Pattern.literal("a").ignore_case())
            '(?i:a)'
        """
        return self.scoped("i")

    def multiline(self) -> Pattern:
        """Make `^` and `$` match at line boundaries."""
        return self.scoped("m")

    def dotall(self) -> Pattern:
        """Make `.` match newlines."""
        return self.scoped("s")

    def lookahead(self) -> Pattern:
        """Assert that this pattern follows, without consuming it."""
        return Pattern(tree.Look(self.node, behind=False, negate=False))

    def negative_lookahead(self) -> Pattern:
        """Assert that this pattern does not follow."""
        return Pattern(tree.Look(self.node, behind=False, negate=True))

    def lookbehind(self) -> Pattern:
        """Assert that this pattern precedes."""
        return Pattern(tree.Look(self.node, behind=True, negate=False))

    def negative_lookbehind(self) -> Pattern:
        """Assert that this pattern does not precede."""
        return Pattern(tree.Look(self.node, behind=True, negate=True))

    def followed_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` follows.

        Example:
            >>> str(Pattern.literal("a").followed_by("b"))
            'a(?=b)'
        """
        return self + Pattern.coerce(other).lookahead()

    def not_followed_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` does not follow.

        Example:
            >>> str(Pattern.literal("a").not_followed_by("b"))
            'a(?!b)'
        """
        return self + Pattern.coerce(other).negative_lookahead()

    def preceded_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` precedes.

        Example:
            >>> str(Pattern.literal("a").preceded_by("b"))
            '(?<=b)a'
        """
        return Pattern.coerce(other).lookbehind() + self

    def not_preceded_by(self, other: Pattern | str) -> Pattern:
        """Match this pattern only when `other` does not precede.

        Example:
            >>> str(Pattern.literal("a").not_preceded_by("b"))
            '(?<!b)a'
        """
        return Pattern.coerce(other).negative_lookbehind() + self

    def optimized(self, level: Level = "safe", flags: int = 0) -> Pattern:
        """Return the cheaper equivalent pattern that `compile` would use.

        `safe` keeps match spans and groups identical. `aggressive` also
        factors and reorders alternatives, which can change which match is
        found, so use it with `fullmatch` or yes/no checks only.

        Example:
            >>> import remagic as rm
            >>> str(rm.any_of("abc").one_or_more().one_or_more().optimized())
            '[abc]++'
        """
        return Pattern(tree.optimize(self.node, level, flags))

    def compile(
        self,
        flags: int = 0,
        *,
        engine: Engine = "auto",
        optimize: bool | Level = True,
    ) -> re.Pattern[str]:
        """Compile with `re`, or with `regex` when the pattern needs it.

        `optimize` rewrites the pattern to a cheaper one with the same
        matches (`True` or `"safe"`), also factors alternatives for
        `fullmatch` use (`"aggressive"`), or compiles the pattern as built
        (`False`).

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
        node = self.node
        if optimize:
            node = tree.optimize(node, "safe" if optimize is True else optimize, flags)
        compiled: re.Pattern[str] = module.compile(tree.render(node), flags)
        return compiled
