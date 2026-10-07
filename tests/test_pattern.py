import re
import sys

import pytest
from hypothesis import given
from hypothesis import strategies as st

import remagic as rm
from remagic import Pattern, RemagicException

TEXT = st.text(min_size=0, max_size=8)


def full(pattern: Pattern, text: str) -> bool:
    return pattern.compile().fullmatch(text) is not None


@given(TEXT)
def test_literal_matches_itself(text: str) -> None:
    assert full(rm.exactly(text), text)


def test_literal_rejects_non_str() -> None:
    with pytest.raises(TypeError):
        Pattern.literal(1)  # type: ignore[arg-type]


@given(TEXT, TEXT)
def test_concat_and_alternation_precedence(a: str, b: str) -> None:
    pattern = (rm.exactly(a) | b) + "z"
    assert full(pattern, a + "z")
    assert full(pattern, b + "z")


def test_alternation_is_wrapped_when_quantified() -> None:
    assert str((rm.exactly("a") | "b").times(2)) == "(?:a|b){2}"


def test_multichar_literal_wrapped_when_quantified() -> None:
    assert full(rm.exactly("ab").times(2), "abab")
    assert not full(rm.exactly("ab").times(2), "abb")


def test_quantified_not_made_possessive_by_requantifying() -> None:
    pattern = rm.exactly("a").one_or_more().one_or_more()
    assert str(pattern) == "(?:a+)+"


def test_empty_pattern_is_identity() -> None:
    a = rm.exactly("a")
    assert Pattern() + a == a
    assert a + Pattern() == a
    assert "" + a == a


def test_radd_ror_and_unsupported_operands() -> None:
    a = rm.exactly("a")
    assert full("x" + a, "xa")
    assert full("x" | a, "x")
    with pytest.raises(TypeError):
        a + 1  # type: ignore[operator]
    with pytest.raises(TypeError):
        a | 1  # type: ignore[operator]
    with pytest.raises(TypeError):
        1 + a  # type: ignore[operator]
    with pytest.raises(TypeError):
        1 | a  # type: ignore[operator]
    with pytest.raises(TypeError):
        a * "x"  # type: ignore[operator]


def test_mul_and_str() -> None:
    assert str(rm.exactly("a") * 3) == "a{3}"


@pytest.mark.parametrize(
    ("build", "source"),
    [
        (lambda p: p.optional(), "a?"),
        (lambda p: p.zero_or_more(), "a*"),
        (lambda p: p.one_or_more(), "a+"),
        (lambda p: p.at_least(3), "a{3,}"),
        (lambda p: p.between(2, 4), "a{2,4}"),
        (lambda p: p.times(0), "a{0}"),
        (lambda p: p.zero_or_more(lazy=True), "a*?"),
        (lambda p: p.one_or_more(possessive=True), "a++"),
    ],
)
def test_quantifier_sources(build, source: str) -> None:  # type: ignore[no-untyped-def]
    assert str(build(rm.exactly("a"))) == source


def test_quantifier_errors() -> None:
    a = rm.exactly("a")
    with pytest.raises(RemagicException):
        a.zero_or_more(lazy=True, possessive=True)
    with pytest.raises(RemagicException):
        a.times(-1)
    with pytest.raises(RemagicException):
        a.between(3, 2)
    with pytest.raises(TypeError):
        a.times(True)
    with pytest.raises(TypeError):
        a.times("2")  # type: ignore[arg-type]


@given(TEXT.filter(bool), st.integers(0, 4))
def test_times_matches_repetition(text: str, count: int) -> None:
    assert full(rm.exactly(text).times(count), text * count)


def test_groups() -> None:
    a = rm.exactly("a")
    assert str(a.group()) == "(a)"
    assert str(a.group("x")) == "(?P<x>a)"
    assert str(a.non_capturing()) == "(?:a)"
    assert str(a.atomic()) == "(?>a)"
    assert a.group("x").compile().fullmatch("a").group("x") == "a"  # type: ignore[union-attr]
    with pytest.raises(RemagicException):
        a.group("1bad")
    with pytest.raises(RemagicException):
        a.group("é")
    with pytest.raises(RemagicException):
        a.group(3)  # type: ignore[arg-type]


def test_scoped_flags() -> None:
    a = rm.exactly("a")
    assert full(a.ignore_case(), "A")
    assert str(a.scoped("i", "s")) == "(?i-s:a)"
    assert str(a.scoped(off="i")) == "(?-i:a)"
    assert full(rm.NEWLINE.dotall(), "\n")
    assert rm.START.multiline().compile().search("x\ny")
    for kwargs in (
        {},
        {"on": "q"},
        {"on": "i", "off": "i"},
        {"off": "a"},
        {"on": "au"},
    ):
        with pytest.raises(RemagicException):
            a.scoped(**kwargs)


def test_lookarounds() -> None:
    a = rm.exactly("a")
    b = rm.exactly("b")
    assert a.followed_by(b).compile().search("ab")
    assert not a.followed_by(b).compile().search("ac")
    assert a.not_followed_by(b).compile().search("ac")
    assert not a.not_followed_by(b).compile().fullmatch("ab")
    assert str(a.preceded_by("b")) == "(?<=b)a"
    assert str(a.not_preceded_by("b")) == "(?<!b)a"
    assert a.preceded_by(b).compile().search("ba")
    assert a.not_preceded_by(b).compile().search("ca")
    assert str(rm.before("b")) == "(?=b)"
    assert str(rm.not_before("b")) == "(?!b)"
    assert str(rm.after("b")) == "(?<=b)"
    assert str(rm.not_after("b")) == "(?<!b)"


def test_assertions_can_be_quantified() -> None:
    assert rm.START.zero_or_more().compile().match("x")
    assert str(rm.WORD_BOUNDARY.optional()) == r"(?:\b)?"


def test_anchors() -> None:
    word = rm.START_OF_STRING + rm.WORD.one_or_more() + rm.END_OF_STRING
    assert word.compile().match("abc")
    assert (rm.WORD_BOUNDARY + "a").compile().search("a")
    assert not (rm.NOT_WORD_BOUNDARY + "a").compile().search("a")
    assert (rm.START + "a" + rm.END).compile().match("a")


def test_constants() -> None:
    assert full(rm.NOT_NEWLINE, "x")
    assert not full(rm.NOT_NEWLINE, "\n")
    assert full(rm.DIGIT.one_or_more(), "123")
    assert full(rm.LETTER, "q")
    assert full(rm.TAB + rm.CARRIAGE_RETURN, "\t\r")


def test_raw_is_wrapped_like_alternation() -> None:
    assert str(rm.raw("a|b") + "c") == "(?:a|b)c"


def test_compile_flags() -> None:
    assert rm.exactly("a").compile(re.IGNORECASE).fullmatch("A")


def test_engine_selection() -> None:
    letter = rm.unicode_property("L")
    assert letter.compile().fullmatch("é")
    assert rm.exactly("a").compile(engine="regex").fullmatch("a")
    with pytest.raises(RemagicException):
        letter.compile(engine="re")
    with pytest.raises(RemagicException):
        rm.exactly("a").compile(engine="nope")  # type: ignore[arg-type]


def test_missing_regex_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "regex", None)
    with pytest.raises(RemagicException, match=r"remagic\[regex\]"):
        rm.unicode_property("L").compile()


def test_needs_regex_propagates() -> None:
    letter = rm.unicode_property("L")
    assert (letter + "a").needs_regex
    assert ("a" + letter).needs_regex
    assert (letter | "a").needs_regex
    assert letter.one_or_more().group().needs_regex
    assert not rm.exactly("a").needs_regex
    assert str(rm.unicode_property("L", negate=True)) == r"\P{L}"
