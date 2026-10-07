"""Syntax tree behind `Pattern`: rendering, analysis and optimisation."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import IntEnum
from functools import cache
from os.path import commonprefix
from typing import Literal

Interval = tuple[int, int]
Mode = Literal["greedy", "lazy", "possessive"]
Level = Literal["safe", "aggressive"]


class Precedence(IntEnum):
    """Binding strength of a pattern, used to decide when to add `(?:...)`."""

    ALTERNATION = 0
    SEQUENCE = 1
    QUANTIFIED = 2
    ATOM = 3


@dataclass(frozen=True, slots=True)
class Lit:
    """Literal text, never empty."""

    text: str


@dataclass(frozen=True, slots=True)
class CharSet:
    """A `[...]` class over sorted, non-touching code point intervals."""

    intervals: tuple[Interval, ...]
    negate: bool = False


@dataclass(frozen=True, slots=True)
class Esc:
    r"""A single-character escape class such as `\\d`, or `.`."""

    token: str


@dataclass(frozen=True, slots=True)
class Assertion:
    r"""A zero-width anchor such as `^` or `\\b`."""

    token: str


@dataclass(frozen=True, slots=True)
class Backref:
    """A reference to a numbered or named group."""

    reference: int | str


@dataclass(frozen=True, slots=True)
class UProp:
    """A Unicode property, which only the `regex` module understands."""

    name: str
    negate: bool


@dataclass(frozen=True, slots=True)
class Raw:
    """Opaque regex source supplied by the user."""

    source: str
    precedence: Precedence
    needs_regex: bool


@dataclass(frozen=True, slots=True)
class Seq:
    """Parts matched one after another."""

    parts: tuple[Node, ...]


@dataclass(frozen=True, slots=True)
class Alt:
    """Alternatives tried in order."""

    parts: tuple[Node, ...]


@dataclass(frozen=True, slots=True)
class Repeat:
    """A quantified child; `high` is None when unbounded."""

    child: Node
    low: int
    high: int | None
    mode: Mode = "greedy"


@dataclass(frozen=True, slots=True)
class Group:
    """A capturing group, named when `name` is set."""

    child: Node
    name: str | None = None


@dataclass(frozen=True, slots=True)
class NonCapture:
    """A `(?:...)` group."""

    child: Node


@dataclass(frozen=True, slots=True)
class Atomic:
    """A `(?>...)` group."""

    child: Node


@dataclass(frozen=True, slots=True)
class Look:
    """A lookahead or lookbehind assertion."""

    child: Node
    behind: bool
    negate: bool


@dataclass(frozen=True, slots=True)
class Scoped:
    """A child with inline flags applied to it alone."""

    child: Node
    on: str
    off: str


Node = (
    Lit
    | CharSet
    | Esc
    | Assertion
    | Backref
    | UProp
    | Raw
    | Seq
    | Alt
    | Repeat
    | Group
    | NonCapture
    | Atomic
    | Look
    | Scoped
)

EMPTY = Seq(())

_NAMED = {"\n": r"\n", "\t": r"\t", "\r": r"\r"}
_CLASS_SPECIAL = frozenset("\\]^-[&~|")


def _hex(char: str) -> str:
    code = ord(char)
    if code <= 0xFF:
        return rf"\x{code:02x}"
    if code <= 0xFFFF:
        return rf"\u{code:04x}"
    return rf"\U{code:08x}"


def _lit_char(char: str) -> str:
    if char in _NAMED:
        return _NAMED[char]
    return re.escape(char) if char.isprintable() else _hex(char)


def _class_char(code: int) -> str:
    char = chr(code)
    if char in _NAMED:
        return _NAMED[char]
    if char in _CLASS_SPECIAL:
        return "\\" + char
    return char if char.isprintable() else _hex(char)


def _interval(low: int, high: int) -> str:
    if high - low < 3:
        return "".join(_class_char(code) for code in range(low, high + 1))
    return f"{_class_char(low)}-{_class_char(high)}"


def make_charset(
    chars: Iterable[str], ranges: Iterable[Interval], negate: bool
) -> CharSet:
    """Build a class from characters and code point ranges, merged and sorted."""
    spans = sorted([*((ord(c), ord(c)) for c in chars), *ranges])
    merged: list[Interval] = []
    for low, high in spans:
        if merged and low <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))
    return CharSet(tuple(merged), negate)


def precedence(node: Node) -> Precedence:
    """How tightly `node` binds when rendered."""
    match node:
        case Lit(text):
            return Precedence.ATOM if len(text) == 1 else Precedence.SEQUENCE
        case Seq():
            return Precedence.SEQUENCE
        case Alt():
            return Precedence.ALTERNATION
        case Repeat() | Look() | Assertion():
            return Precedence.QUANTIFIED
        case Raw(_, level, _):
            return level
        case _:
            return Precedence.ATOM


def wrap(node: Node, minimum: Precedence) -> str:
    """Render `node`, adding `(?:...)` if it binds looser than `minimum`."""
    source = render(node)
    if precedence(node) >= minimum:
        return source
    return f"(?:{source})"


def _suffix(low: int, high: int | None, mode: Mode) -> str:
    if high is None:
        text = {0: "*", 1: "+"}.get(low, f"{{{low},}}")
    elif (low, high) == (0, 1):
        text = "?"
    elif low == high:
        text = f"{{{low}}}"
    else:
        text = f"{{{low},{high}}}"
    return text + {"greedy": "", "lazy": "?", "possessive": "+"}[mode]


def render(node: Node) -> str:
    """Regex source for `node`."""
    match node:
        case Lit(text):
            return "".join(_lit_char(char) for char in text)
        case CharSet(intervals, negate):
            body = "".join(_interval(low, high) for low, high in intervals)
            return f"[{'^' if negate else ''}{body}]"
        case Esc(token) | Assertion(token):
            return token
        case Backref(int() as number):
            return rf"(?:\{number})"
        case Backref(name):
            return f"(?P={name})"
        case UProp(name, negate):
            return f"\\{'P' if negate else 'p'}{{{name}}}"
        case Raw(source, _, _):
            return source
        case Seq(parts):
            return "".join(wrap(part, Precedence.SEQUENCE) for part in parts)
        case Alt(parts):
            return "|".join(render(part) for part in parts)
        case Repeat(child, low, high, mode):
            return wrap(child, Precedence.ATOM) + _suffix(low, high, mode)
        case Group(child, None):
            return f"({render(child)})"
        case Group(child, name):
            return f"(?P<{name}>{render(child)})"
        case NonCapture(child):
            return f"(?:{render(child)})"
        case Atomic(child):
            return f"(?>{render(child)})"
        case Look(child, behind, negate):
            return f"(?{'<' if behind else ''}{'!' if negate else '='}{render(child)})"
        case Scoped(child, on, off):
            return f"(?{on}{'-' + off if off else ''}:{render(child)})"
    raise AssertionError(node)  # pragma: no cover


def children(node: Node) -> tuple[Node, ...]:
    """Direct children of `node`."""
    match node:
        case Seq(parts) | Alt(parts):
            return parts
        case Repeat(child, _, _, _) | Group(child, _) | NonCapture(child):
            return (child,)
        case Atomic(child) | Look(child, _, _) | Scoped(child, _, _):
            return (child,)
        case _:
            return ()


def contains(node: Node, kinds: tuple[type, ...]) -> bool:
    """Whether `node` or any descendant is one of `kinds`."""
    return isinstance(node, kinds) or any(contains(c, kinds) for c in children(node))


def needs_regex(node: Node) -> bool:
    """Whether only the `regex` module can compile `node`."""
    if isinstance(node, UProp) or (isinstance(node, Raw) and node.needs_regex):
        return True
    return any(needs_regex(child) for child in children(node))


# --- optimisation ----------------------------------------------------------

_LOOSE = re.I | re.A | re.L | re.S
_DISJOINT_ESCAPES = (
    frozenset({r"\d", r"\D"}),
    frozenset({r"\w", r"\W"}),
    frozenset({r"\s", r"\S"}),
    frozenset({r"\d", r"\W"}),
    frozenset({r"\d", r"\s"}),
)
_SCAN_LIMIT = 4096

Atom = tuple[str, object]
First = tuple[tuple[Atom, ...] | None, bool]


def _single(node: Node) -> bool:
    return (isinstance(node, Lit) and len(node.text) == 1) or isinstance(
        node, CharSet | Esc
    )


def _unit(node: Node) -> tuple[Node, int, int | None] | None:
    if isinstance(node, Repeat) and node.mode == "greedy" and _single(node.child):
        return node.child, node.low, node.high
    if _single(node):
        return node, 1, 1
    return None


_UNROLL_LIMIT = 64


def _unrolled(repeat: Repeat) -> Node:
    child = repeat.child
    if (
        isinstance(child, Lit)
        and repeat.low == repeat.high
        and repeat.low * len(child.text) <= _UNROLL_LIMIT
    ):
        return Lit(child.text * repeat.low)
    return repeat


def _merge(left: Node, right: Node) -> Node | None:
    if isinstance(left, Lit) and isinstance(right, Lit):
        return Lit(left.text + right.text)
    first, second = _unit(left), _unit(right)
    if first is None or second is None or first[0] != second[0]:
        return None
    high = None if first[2] is None or second[2] is None else first[2] + second[2]
    return _unrolled(Repeat(first[0], first[1] + second[1], high))


def _seq(parts: Iterable[Node]) -> Node:
    out: list[Node] = []
    for part in parts:
        for piece in part.parts if isinstance(part, Seq) else (part,):
            merged = _merge(out[-1], piece) if out else None
            if merged is None:
                out.append(piece)
            else:
                out[-1] = merged
    if len(out) == 1:
        return out[0]
    return Seq(tuple(out))


def _as_chars(node: Node) -> tuple[Interval, ...] | None:
    if isinstance(node, Lit) and len(node.text) == 1:
        return ((ord(node.text), ord(node.text)),)
    if isinstance(node, CharSet) and not node.negate:
        return node.intervals
    return None


def _merge_chars(parts: list[Node]) -> list[Node]:
    out: list[Node] = []
    run: list[Interval] = []

    def flush() -> None:
        if len(run) == 1 and run[0][0] == run[0][1]:
            out.append(Lit(chr(run[0][0])))
        elif run:
            out.append(make_charset((), run, negate=False))
        run.clear()

    for part in parts:
        spans = _as_chars(part)
        if spans is None:
            flush()
            out.append(part)
        else:
            run.extend(spans)
    flush()
    return out


def _factor(texts: list[str], reorder: bool) -> list[Node]:
    groups: list[list[str]] = []
    for text in texts:
        for group in groups if reorder else groups[-1:]:
            if group[0][0] == text[0]:
                group.append(text)
                break
        else:
            groups.append([text])
    out: list[Node] = []
    for group in groups:
        if len(group) == 1:
            out.append(Lit(group[0]))
            continue
        prefix = commonprefix(group)
        rest = tuple(Lit(t[len(prefix) :]) if t != prefix else EMPTY for t in group)
        out.append(Seq((Lit(prefix), Alt(rest))))
    return out


def _factor_runs(parts: list[Node], reorder: bool) -> list[Node]:
    out: list[Node] = []
    run: list[str] = []
    for part in [*parts, EMPTY]:
        if isinstance(part, Lit):
            run.append(part.text)
            continue
        if run:
            out.extend(_factor(run, reorder))
            run = []
        out.append(part)
    return out[:-1]


def _alt(parts: Iterable[Node], aggressive: bool, ordered_ok: bool) -> Node:
    flat: list[Node] = []
    for part in parts:
        for piece in part.parts if isinstance(part, Alt) else (part,):
            if not (piece in flat and not contains(piece, (Group,))):
                flat.append(piece)
    if aggressive:
        lits = [p for p in flat if isinstance(p, Lit)]
        if lits:
            first = flat.index(lits[0])
            rest = [p for p in flat if not isinstance(p, Lit)]
            flat = [*rest[:first], *lits, *rest[first:]]
    flat = _factor_runs(_merge_chars(flat), aggressive or ordered_ok)
    if len(flat) == 1:
        return flat[0]
    return Alt(tuple(flat))


def _folded(
    inner: Repeat, low: int, high: int | None, aggressive: bool
) -> tuple[int, int | None] | None:
    in_low, in_high = inner.low, inner.high
    if in_high is None and in_low <= 1 and high is None:
        return low * in_low, None
    if (in_low, in_high) == (0, 1) and high is None:
        return 0, None
    if (low, high) == (0, 1) and in_high is None and in_low <= 1:
        return 0, None
    if (low, high) == (0, 1) and (in_low, in_high) == (0, 1):
        return 0, 1
    if (
        aggressive
        and high is not None
        and in_high is not None
        and (high == low or (low + 1) * in_low <= low * in_high + 1)
    ):
        return low * in_low, high * in_high
    return None


def _repeat(
    child: Node, low: int, high: int | None, mode: Mode, aggressive: bool
) -> Node:
    captures = contains(child, (Group,))
    if child == EMPTY:
        return EMPTY
    if (low, high) == (1, 1):
        return child
    if (low, high) == (0, 0) and not captures:
        return EMPTY
    if isinstance(child, Repeat) and not captures:
        if child.low == child.high and low == high and high is not None:
            product = child.low * high
            return _unrolled(Repeat(child.child, product, product))
        if mode == child.mode == "greedy" and _single(child.child):
            fold = _folded(child, low, high, aggressive)
            if fold is not None:
                return Repeat(child.child, *fold)
    return _unrolled(Repeat(child, low, high, mode))


def _atomic(child: Node) -> Node:
    if (
        isinstance(child, Atomic | Lit)
        or _single(child)
        or (isinstance(child, Repeat) and child.mode == "possessive")
    ):
        return child
    return Atomic(child)


def _simplify(node: Node, aggressive: bool, ordered_ok: bool) -> Node:
    def go(child: Node) -> Node:
        return _simplify(child, aggressive, ordered_ok)

    match node:
        case Seq(parts):
            return _seq(go(part) for part in parts)
        case Alt(parts):
            return _alt((go(part) for part in parts), aggressive, ordered_ok)
        case Repeat(child, low, high, mode):
            return _repeat(go(child), low, high, mode, aggressive)
        case Group(child, name):
            return Group(go(child), name)
        case NonCapture(child):
            return go(child)
        case Atomic(child):
            return _atomic(go(child))
        case Look(child, behind, negate):
            return Look(go(child), behind, negate)
        case Scoped(child, on, off):
            return Scoped(go(child), on, off)
        case _:
            return node


@cache
def _escape_matcher(token: str) -> re.Pattern[str]:
    return re.compile(token)


def _covered(low: int, high: int, intervals: tuple[Interval, ...]) -> bool:
    return any(a <= low and high <= b for a, b in intervals)


def _disjoint_atoms(left: Atom, right: Atom) -> bool:
    (kind_a, value_a), (kind_b, value_b) = left, right
    if kind_a == "esc" and kind_b == "esc":
        return frozenset({value_a, value_b}) in _DISJOINT_ESCAPES
    if kind_a == "esc":
        return _disjoint_atoms(right, left)
    spans: tuple[Interval, ...] = value_a  # type: ignore[assignment]
    if kind_b == "esc":
        if kind_a == "neg" or sum(b - a + 1 for a, b in spans) > _SCAN_LIMIT:
            return False
        matcher = _escape_matcher(str(value_b))
        return not any(
            matcher.fullmatch(chr(code)) for a, b in spans for code in range(a, b + 1)
        )
    others: tuple[Interval, ...] = value_b  # type: ignore[assignment]
    if kind_a == "pos" and kind_b == "pos":
        return not any(a <= d and c <= b for a, b in spans for c, d in others)
    if kind_a == "pos":
        return all(_covered(a, b, others) for a, b in spans)
    if kind_b == "pos":
        return all(_covered(c, d, spans) for c, d in others)
    return False


def _disjoint(left: tuple[Atom, ...], right: tuple[Atom, ...]) -> bool:
    return all(_disjoint_atoms(a, b) for a in left for b in right)


def _first(node: Node) -> First:
    match node:
        case Lit(text):
            return ((("pos", ((ord(text[0]),) * 2,)),), False)
        case CharSet(intervals, negate):
            return (("neg" if negate else "pos", intervals),), False
        case Esc(token):
            return (("esc", token),), False
        case Seq(parts):
            atoms: tuple[Atom, ...] = ()
            for part in parts:
                found, nullable = _first(part)
                if found is None:
                    return None, False
                atoms += found
                if not nullable:
                    return atoms, False
            return atoms, True
        case Alt(parts):
            atoms = ()
            nullable = False
            for part in parts:
                found, part_nullable = _first(part)
                if found is None:
                    return None, False
                atoms += found
                nullable = nullable or part_nullable
            return atoms, nullable
        case Repeat(child, low, _, _):
            found, nullable = _first(child)
            return found, nullable or low == 0
        case Group(child, _):
            return _first(child)
        case _:
            return None, False


def _follow(rest: tuple[Node, ...], after: tuple[Atom, ...] | None):  # type: ignore[no-untyped-def]
    atoms: tuple[Atom, ...] = ()
    for part in rest:
        found, nullable = _first(part)
        if found is None:
            return None
        atoms += found
        if not nullable:
            return atoms
    return None if after is None else atoms + after


def _possess(node: Node, after: tuple[Atom, ...] | None) -> Node:
    match node:
        case Seq(parts):
            return Seq(
                tuple(
                    _possess(part, _follow(parts[i + 1 :], after))
                    for i, part in enumerate(parts)
                )
            )
        case Alt(parts):
            return Alt(tuple(_possess(part, after) for part in parts))
        case Group(child, name):
            return Group(_possess(child, after), name)
        case Atomic(child):
            return Atomic(_possess(child, ()))
        case Look(child, behind, negate):
            return Look(_possess(child, ()), behind, negate)
        case Repeat(child, low, high, "greedy"):
            if _single(child) and low != high and after is not None:
                first, _ = _first(child)
                if first is not None and _disjoint(first, after):
                    return Repeat(child, low, high, "possessive")
            return Repeat(_possess(child, None), low, high, "greedy")
        case Repeat(child, low, high, mode):
            return Repeat(_possess(child, None), low, high, mode)
        case _:
            return node


def optimize(
    node: Node, level: Level = "safe", flags: int = 0, *, possessive: bool = True
) -> Node:
    """Return a cheaper tree that matches the same way.

    `safe` keeps match spans and groups identical to the input. `aggressive`
    only keeps the language, so it is valid for `fullmatch` and yes/no checks.
    `possessive=False` skips the possessive rewrite, which the `regex` module
    runs slower than plain greedy repeats.
    """
    aggressive = level == "aggressive"
    sets_known = not (contains(node, (Raw, Scoped)) or flags & _LOOSE)
    while True:
        simpler = _simplify(node, aggressive, sets_known)
        if simpler == node:
            break
        node = simpler
    return _possess(node, ()) if sets_known and possessive else node
