import re
import time

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import remagic as rm
from remagic import Pattern, unsafe
from remagic import _tree as tree

ALPHABET = "abc"
LEAVES = st.one_of(
    st.text(ALPHABET, min_size=1, max_size=3).map(rm.exactly),
    st.sampled_from([rm.DIGIT, rm.WORD, rm.CHAR, rm.NOT_WS]),
    st.sets(st.sampled_from("abc1 "), min_size=1).map(rm.char_in),
    st.sets(st.sampled_from("ab"), min_size=1).map(rm.char_not_in),
)


def _wrap(children: st.SearchStrategy[Pattern]) -> st.SearchStrategy[Pattern]:
    counts = st.integers(0, 3)
    return st.one_of(
        st.tuples(children, children).map(lambda t: t[0] + t[1]),
        st.tuples(children, children).map(lambda t: t[0] | t[1]),
        st.tuples(children, st.booleans()).map(
            lambda t: t[0].group() if t[1] else t[0].non_capturing()
        ),
        st.tuples(children, counts, counts, st.sampled_from(["g", "l"])).map(
            lambda t: t[0].between(min(t[1], t[2]), max(t[1], t[2]), lazy=t[3] == "l")
        ),
        children.map(lambda p: p.one_or_more()),
        children.map(lambda p: p.zero_or_more()),
        children.map(lambda p: p.optional()),
        children.map(lambda p: p.atomic()),
        children.map(lambda p: p.followed_by("a")),
        children.map(lambda p: p.not_followed_by("b")),
    )


TREES = st.recursive(LEAVES, _wrap, max_leaves=6)
INPUTS = st.text("abc1 \n", max_size=7)


def _spans(pattern: re.Pattern[str], text: str) -> list[tuple[object, ...]]:
    return [(m.span(), m.groups()) for m in pattern.finditer(text)]


@settings(max_examples=400, deadline=None)
@given(TREES, INPUTS)
def test_safe_optimisation_keeps_every_match_and_group(
    pattern: Pattern, text: str
) -> None:
    plain = pattern.compile(optimize=False)
    fast = pattern.compile()
    assert _spans(plain, text) == _spans(fast, text)
    assert plain.groups == fast.groups


@settings(max_examples=400, deadline=None)
@given(TREES, INPUTS)
def test_aggressive_optimisation_keeps_the_language(
    pattern: Pattern, text: str
) -> None:
    plain = pattern.compile(optimize=False)
    fast = pattern.compile(optimize="aggressive")
    assert bool(plain.fullmatch(text)) == bool(fast.fullmatch(text))
    assert bool(plain.search(text)) == bool(fast.search(text))


a, b, c = rm.exactly("a"), rm.exactly("b"), rm.exactly("c")


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        (a | b | c, "[abc]"),
        (rm.any_of("abd"), "[abd]"),
        (a.one_or_more().non_capturing().one_or_more(), "a++"),
        (a.times(2).non_capturing().times(3), "a{6}"),
        (a.one_or_more() + a.one_or_more(), "a{2,}+"),
        (a + a + a, "aaa"),
        (a.zero_or_more() + a, "a++"),
        (a.optional().optional(), "a?+"),
        (a.zero_or_more().optional(), "a*+"),
        (a.times(0), ""),
        (a | a, "a"),
        (a.non_capturing(), "a"),
        (a.times(1), "a"),
        (a.atomic(), "a"),
        (a.atomic().atomic(), "a"),
        (rm.DIGIT.one_or_more() + "x", r"\d++x"),
        (rm.DIGIT.one_or_more() + "5", r"\d+5"),
        (rm.DIGIT.one_or_more() + rm.WORD, r"\d+\w"),
        (rm.DIGIT.one_or_more() + rm.NOT_WORD, r"\d++\W"),
        (rm.WORD.one_or_more() + rm.NOT_WS, r"\w+\S"),
        (rm.char_in("ab").one_or_more() + "c", "[ab]++c"),
        (rm.char_in("ab").one_or_more() + rm.char_not_in("ab"), "[ab]++[^ab]"),
        (rm.char_not_in("ab").one_or_more() + "a", "[^ab]++a"),
        (rm.char_not_in("a").one_or_more() + rm.char_not_in("b"), "[^a]+[^b]"),
        (rm.char_in("ab").one_or_more() + rm.DIGIT, "[ab]++\\d"),
        (rm.NOT_WS.one_or_more() + rm.DIGIT, r"\S+\d"),
        (rm.DIGIT.one_or_more() + rm.WS, r"\d++\s"),
        (rm.CHAR.one_or_more() + "x", ".+x"),
        (rm.DIGIT.one_or_more().group() + "x", r"(\d++)x"),
        (a.group().one_or_more().non_capturing(), "(a)+"),
        (a.group().times(0), "(a){0}"),
        (rm.START + a.one_or_more(), "^a++"),
        (a.one_or_more().lookahead(), "(?=a++)"),
        (a.scoped("i"), "(?i:a)"),
        (a.one_or_more() + unsafe.raw("x"), "a+(?:x)"),
    ],
)
def test_safe_forms(pattern: Pattern, expected: str) -> None:
    assert str(pattern.optimized()) == expected


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        (rm.exactly("foobar") | "foobaz", "fooba[rz]"),
        (rm.exactly("foo") | "foobar", "foo(?:|bar)"),
        (rm.exactly("ab") | "c" | "ad", "a[bd]|c"),
        (rm.exactly("ab") | rm.DIGIT | "ac", "a[bc]|\\d"),
    ],
)
def test_aggressive_forms(pattern: Pattern, expected: str) -> None:
    assert str(pattern.optimized("aggressive")) == expected


def test_safe_level_never_changes_match_priority() -> None:
    pattern = rm.exactly("a") | "ab"
    assert pattern.compile().match("ab").group() == "a"  # type: ignore[union-attr]


def test_str_shows_the_built_structure() -> None:
    assert str(a | b | c) == "a|b|c"


def test_optimisation_is_idempotent_and_skipped_for_raw() -> None:
    pattern = (a | b).one_or_more() + rm.DIGIT
    once = pattern.optimized()
    assert once.optimized() == once
    assert str(unsafe.raw("(a+)+").optimized()) == "(a+)+"


def _time(compiled: re.Pattern[str], text: str) -> float:
    start = time.perf_counter()
    compiled.fullmatch(text)
    return time.perf_counter() - start


def test_nested_quantifiers_no_longer_backtrack_catastrophically() -> None:
    pattern = a.one_or_more().non_capturing().one_or_more() + "c"
    text = "a" * 5000 + "b"
    assert _time(pattern.compile(), text) < 0.5


def test_unoptimised_nested_quantifier_is_the_slow_baseline() -> None:
    pattern = a.one_or_more().non_capturing().one_or_more() + "c"
    slow = _time(pattern.compile(optimize=False), "a" * 22 + "b")
    fast = _time(pattern.compile(), "a" * 22 + "b")
    assert fast * 20 < slow


def test_tree_helpers() -> None:
    assert tree.contains(tree.Group(tree.Lit("a")), (tree.Group,))
    assert tree.needs_regex(tree.Seq((tree.Lit("a"), tree.UProp("L", False))))
    assert tree.make_charset("ba", [(100, 101)], False).intervals == (
        (97, 98),
        (100, 101),
    )


d = rm.DIGIT.one_or_more()


@pytest.mark.parametrize(
    ("rest", "expected"),
    [
        (rm.WS + "y", r"\d++\sy"),
        (rm.WS.optional() + "y", r"\d++\s?+y"),
        (rm.WS.optional() + rm.NOT_WS, r"\d+\s?+\S"),
        (unsafe.raw("q") + "y", r"\d+(?:q)y"),
        (rm.WS | "xy", r"\d++(?:\s|xy)"),
        (rm.WS.optional() | "xy", r"\d++(?:\s?+|xy)"),
        (unsafe.raw("q") | "xy", r"\d+(?:q|xy)"),
        (rm.WS.zero_or_more().group() + "y", r"\d++(\s*+)y"),
        (rm.before("y"), r"\d+(?=y)"),
        ((rm.WS + "y").group(), r"\d++(\sy)"),
        ((rm.WS.optional() + "y").group(), r"\d++(\s?+y)"),
        ((rm.before("q") + "y").group(), r"\d+((?=q)y)"),
        ((rm.before("q") | "xy").group(), r"\d+((?=q)|xy)"),
        (rm.char_not_in("a").group(), r"\d+([^a])"),
        (rm.char_range("\x00", "\uffff").group(), r"\d+([\x00-\uffff])"),
    ],
)
def test_possessive_looks_through_what_follows(rest: Pattern, expected: str) -> None:
    assert str((d + rest).optimized()) == expected


def test_precedence_property() -> None:
    assert a.precedence is tree.Precedence.ATOM
    assert (a | b).precedence is tree.Precedence.ALTERNATION


def test_possessive_rewrite_is_for_the_stdlib_engine_only() -> None:
    pattern = rm.DIGIT.one_or_more() + "x"
    assert pattern.compile(engine="re").pattern == r"\d++x"
    assert pattern.compile(engine="regex").pattern == r"\d+x"
