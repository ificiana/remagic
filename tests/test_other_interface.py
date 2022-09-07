import pytest

from remagic import *


@pytest.mark.parametrize(
    "iterable, expected_output",
    [
        ("test", "[tes]"),
        (".", r"[.]"),
        (["a", "e", "i", "o", "u"], "[aeiou]"),
        ({1: "one", 2: "two"}, "[12]"),
        ({1: "one", 2: "two"}.values(), "[onetw]"),
    ],
)
def test_char_in(iterable, expected_output):
    output = char_in(iterable)
    assert output._pattern == expected_output, "{} != {}".format(
        output, expected_output
    )


@pytest.mark.parametrize(
    "iterable, expected_output",
    [
        ("test", "[^tes]"),
        (".", r"[^.]"),
        (["a", "e", "i", "o", "u"], "[^aeiou]"),
        ({1: "one", 2: "two"}, "[^12]"),
        ({1: "one", 2: "two"}.values(), "[^onetw]"),
    ],
)
def test_char_not_in(iterable, expected_output):
    output = char_not_in(iterable)
    assert output._pattern == expected_output, "{} != {}".format(
        output, expected_output
    )


@pytest.mark.parametrize(
    "iterable, expected_output",
    [
        ("test", "t|e|s"),
        (".", r"\."),
        (["a", "e", "i", "o", "u"], "a|e|i|o|u"),
        ({1: "one", 2: "two"}, "1|2"),
        ({1: "one", 2: "two"}.values(), "one|two"),
    ],
)
def test_char_in(iterable, expected_output):
    output = any_of(iterable)
    assert output._pattern == expected_output, "{} != {}".format(
        output, expected_output
    )
