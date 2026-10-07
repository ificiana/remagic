"""Free-function builders; each mirrors a :class:`Pattern` method."""

from __future__ import annotations

from collections.abc import Iterable

from .exceptions import RemagicException
from .pattern import Pattern, Precedence, class_escape


def create(value: Pattern | str) -> Pattern:
    """Return `value` as a pattern; strings are matched literally."""
    return Pattern.coerce(value)


def exactly(text: str) -> Pattern:
    """Match `text` literally."""
    return Pattern.literal(text)


def raw(source: str, *, needs_regex: bool = False) -> Pattern:
    """Use existing regex source as-is."""
    return Pattern.raw(source, needs_regex=needs_regex)


def optional(
    value: Pattern | str, *, lazy: bool = False, possessive: bool = False
) -> Pattern:
    """Zero or one of `value`."""
    return create(value).optional(lazy=lazy, possessive=possessive)


def zero_or_more(
    value: Pattern | str, *, lazy: bool = False, possessive: bool = False
) -> Pattern:
    """Zero or more of `value`."""
    return create(value).zero_or_more(lazy=lazy, possessive=possessive)


def one_or_more(
    value: Pattern | str, *, lazy: bool = False, possessive: bool = False
) -> Pattern:
    """One or more of `value`."""
    return create(value).one_or_more(lazy=lazy, possessive=possessive)


def times(
    value: Pattern | str, count: int, *, lazy: bool = False, possessive: bool = False
) -> Pattern:
    """Exactly `count` of `value`."""
    return create(value).times(count, lazy=lazy, possessive=possessive)


def between(
    value: Pattern | str,
    low: int,
    high: int,
    *,
    lazy: bool = False,
    possessive: bool = False,
) -> Pattern:
    """`low` to `high` of `value`."""
    return create(value).between(low, high, lazy=lazy, possessive=possessive)


def at_least(
    value: Pattern | str, low: int, *, lazy: bool = False, possessive: bool = False
) -> Pattern:
    """`low` or more of `value`."""
    return create(value).at_least(low, lazy=lazy, possessive=possessive)


def group(value: Pattern | str, name: str | None = None) -> Pattern:
    """Capture `value`, optionally under `name`."""
    return create(value).group(name)


def non_capturing(value: Pattern | str) -> Pattern:
    """Group `value` without capturing."""
    return create(value).non_capturing()


def atomic(value: Pattern | str) -> Pattern:
    """Group `value` so it is never backtracked into."""
    return create(value).atomic()


def scoped(value: Pattern | str, on: str = "", off: str = "") -> Pattern:
    """Apply inline flags to `value` only."""
    return create(value).scoped(on, off)


def any_of(values: Iterable[Pattern | str]) -> Pattern:
    r"""Match any one of `values`, trying them in order.

    >>> str(any_of(["a.b", "c"]))
    'a\\.b|c'
    """
    unique: dict[str, Pattern] = {}
    for value in values:
        item = create(value)
        unique.setdefault(item.source, item)
    if not unique:
        raise RemagicException("any_of needs at least one alternative")
    result, *rest = unique.values()
    for item in rest:
        result |= item
    return result


def _class(
    chars: Iterable[str], ranges: Iterable[tuple[str, str]], negate: bool
) -> Pattern:
    body = "".join(dict.fromkeys(class_escape(char) for char in chars))
    for low, high in ranges:
        if len(low) != 1 or len(high) != 1 or low > high:
            raise RemagicException(f"invalid range: {low!r}-{high!r}")
        body += f"{class_escape(low)}-{class_escape(high)}"
    if not body:
        raise RemagicException("a character class needs at least one member")
    return Pattern(f"[{'^' if negate else ''}{body}]", Precedence.ATOM)


def char_in(chars: Iterable[str], *, ranges: Iterable[tuple[str, str]] = ()) -> Pattern:
    """Match one character from `chars` or from the inclusive `ranges`."""
    return _class(chars, ranges, negate=False)


def char_not_in(
    chars: Iterable[str], *, ranges: Iterable[tuple[str, str]] = ()
) -> Pattern:
    """Match one character that is not in `chars` or `ranges`."""
    return _class(chars, ranges, negate=True)


def char_range(low: str, high: str) -> Pattern:
    """Match one character from `low` to `high`, inclusive."""
    return _class((), [(low, high)], negate=False)


def unicode_property(name: str, *, negate: bool = False) -> Pattern:
    r"""Match a Unicode property such as `L` or `Greek`; needs `regex`."""
    if not name or "}" in name:
        raise RemagicException(f"invalid Unicode property: {name!r}")
    return Pattern(f"\\{'P' if negate else 'p'}{{{name}}}", Precedence.ATOM, True)


def before(value: Pattern | str) -> Pattern:
    """Assert that `value` follows the current position."""
    return create(value).lookahead()


def not_before(value: Pattern | str) -> Pattern:
    """Assert that `value` does not follow the current position."""
    return create(value).negative_lookahead()


def after(value: Pattern | str) -> Pattern:
    """Assert that `value` precedes the current position."""
    return create(value).lookbehind()


def not_after(value: Pattern | str) -> Pattern:
    """Assert that `value` does not precede the current position."""
    return create(value).negative_lookbehind()


def ref(reference: int | str) -> Pattern:
    """Match the text captured by a numbered or named group."""
    if isinstance(reference, bool):
        raise RemagicException("references are positive integers or group names")
    if isinstance(reference, int) and reference > 0:
        return Pattern(rf"(?:\{reference})", Precedence.ATOM)
    if isinstance(reference, str) and reference.isidentifier() and reference.isascii():
        return Pattern(f"(?P={reference})", Precedence.ATOM)
    raise RemagicException("references are positive integers or group names")
