import pytest
from hypothesis import given
from hypothesis import strategies as st

import remagic as rm
from remagic import RemagicException

CHARS = st.text(min_size=1, max_size=6)


def full(pattern: rm.Pattern, text: str) -> bool:
    return pattern.compile().fullmatch(text) is not None


def test_create() -> None:
    a = rm.exactly("a")
    assert rm.create(a) is a
    assert rm.create("a.") == rm.exactly("a.")


@given(CHARS)
def test_char_in_matches_each_member(chars: str) -> None:
    cls = rm.char_in(chars)
    assert all(full(cls, c) for c in chars)


@given(CHARS)
def test_char_not_in_rejects_members(chars: str) -> None:
    cls = rm.char_not_in(chars)
    assert not any(full(cls, c) for c in chars)


def test_char_class_specials_and_ranges() -> None:
    assert full(rm.char_in("^]-\\[&~|"), "]")
    assert full(rm.char_in("a", ranges=[("0", "9")]), "5")
    assert full(rm.char_range("a", "c"), "b")
    assert not full(rm.char_range("a", "c"), "d")
    assert str(rm.char_in("aab")) == "[ab]"


@pytest.mark.parametrize("ranges", [[("a", "")], [("ab", "c")], [("z", "a")]])
def test_invalid_ranges(ranges: list[tuple[str, str]]) -> None:
    with pytest.raises(RemagicException):
        rm.char_in("", ranges=ranges)


def test_empty_class() -> None:
    with pytest.raises(RemagicException):
        rm.char_in("")


@given(st.lists(CHARS, min_size=1, max_size=4))
def test_any_of_matches_every_alternative(items: list[str]) -> None:
    pattern = rm.any_of(items)
    assert all(full(pattern, item) for item in items)


def test_any_of_dedups_and_mixes() -> None:
    assert str(rm.any_of(["a", "a", rm.DIGIT])) == r"a|\d"
    assert str(rm.any_of(["a"])) == "a"
    assert str(rm.any_of(["a.b"])) == r"a\.b"
    with pytest.raises(RemagicException):
        rm.any_of([])


def test_free_function_quantifiers() -> None:
    assert str(rm.optional("a")) == "a?"
    assert str(rm.zero_or_more("a", lazy=True)) == "a*?"
    assert str(rm.one_or_more("a", possessive=True)) == "a++"
    assert str(rm.times("a", 2)) == "a{2}"
    assert str(rm.between("a", 1, 2)) == "a{1,2}"
    assert str(rm.at_least("a", 2)) == "a{2,}"


def test_free_function_groups() -> None:
    assert str(rm.group("a")) == "(a)"
    assert str(rm.group("a", "n")) == "(?P<n>a)"
    assert str(rm.non_capturing("ab")) == "(?:ab)"
    assert str(rm.atomic("a")) == "(?>a)"
    assert str(rm.scoped("a", "i")) == "(?i:a)"


def test_unicode_property() -> None:
    assert full(rm.unicode_property("Greek"), "\u03b1")
    for name in ("", "a}"):
        with pytest.raises(RemagicException):
            rm.unicode_property(name)


def test_refs() -> None:
    doubled = rm.group(rm.WORD.one_or_more()) + " " + rm.ref(1)
    assert full(doubled, "ab ab")
    assert not full(doubled, "ab cd")
    named = rm.group(rm.DIGIT, "d") + rm.ref("d")
    assert full(named, "77")
    assert full(rm.group("a") + rm.ref(1) + "2", "aa2")
    for bad in (0, -1, True, 1.5, "1x", "é"):
        with pytest.raises(RemagicException):
            rm.ref(bad)  # type: ignore[arg-type]


def test_readme_example() -> None:
    year = rm.DIGIT.times(4).group("year")
    date = year + "-" + rm.DIGIT.times(2).group("month")
    match = date.compile().fullmatch("2027-01")
    assert match
    assert match["year"] == "2027"


def test_version() -> None:
    assert isinstance(rm.__version__, str)
