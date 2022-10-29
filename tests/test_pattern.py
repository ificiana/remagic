# flake8: noqa

import pytest

from remagic import *
from remagic.exceptions import RemagicException


@pytest.mark.parametrize(
    "input_pattern1, input_pattern2, expected_output",
    [
        ("test", "test", "testtest"),
        (".", ".", ".."),
        (CHAR, ".", ".."),
        (CHAR, WS, r".\s"),
        ("test", CHAR, "test."),
    ],
)
def test_pattern_addition(input_pattern1, input_pattern2, expected_output):
    """
    :param input_pattern1: 1st pattern.
    :param input_pattern2: 2nd pattern.
    :param expected_output: The expected transformation.
    """
    output = create(input_pattern1) + create(input_pattern2)
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "input_pattern, expected_output",
    [
        ("test", "test"),
        (".", "."),
        (CHAR, "."),
        (WS, r"\s"),
    ],
)
def test_pattern(input_pattern, expected_output):
    """
    :param input_pattern: Pattern.
    :param expected_output: The expected transformation.
    """
    output = create("")
    ex1 = create(input_pattern).pattern
    output.pattern = create(input_pattern).pattern
    ex2 = output.pattern

    assert (ex1, ex2) == (
        expected_output,
        expected_output,
    ), f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "const, expected_output",
    [
        (CHAR, "."),
        (WS, r"\s"),
        (N, r"\n"),
    ],
)
def test_create_constants(const, expected_output):
    """
    :param const: Constant
    :param expected_output: The expected transformation.
    """
    output = const._pattern
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("test", "test"),
        (".", "."),
        (r"a sentence\.", r"a sentence\."),
        (CHAR, "."),
    ],
)
def test_create_pattern(input_str, expected_output):
    """
    :param input_str: String to transform.
    :param expected_output: The expected transformation.
    """
    output = create(input_str)._pattern
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "input_str1, input_str2, expected_output",
    [
        ("test", "test", "testtest"),
        (".", ".", ".."),
        (CHAR, ".", r".."),
        (".", str(CHAR), r".."),
        (CHAR, N, r".\n"),
    ],
)
def test_add_patterns_within_create(input_str1, input_str2, expected_output):
    """
    :param input_str1: 1st String to transform.
    :param input_str2: 2nd String to transform.
    :param expected_output: The expected transformation.
    """
    output = create(input_str1 + input_str2)._pattern
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "input_str, num, expected_output",
    [
        ("test", 2, "testtest"),
        (CHAR, 2, ".{2}"),
    ],
)
def test_multiply_patterns_within_create(input_str, num, expected_output):
    """
    :param input_str: 1st String to transform.
    :param num: multiplier
    :param expected_output: The expected transformation.
    """
    output = create(input_str * num)._pattern
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "input_str, num, expected_output",
    [
        ("test", 2, "testtest"),
        (CHAR, 2, ".{2}"),
        (WS, (2, 5), r"\s{2,5}"),
        (DIGIT, (0,), r"\d*"),
        (DIGIT, (1,), r"\d+"),
        (DIGIT, (0, 1), r"\d?"),
    ],
)
def test_repeat(input_str, num, expected_output):
    """
    :param input_str: 1st String to transform.
    :param num: multiplier
    :param expected_output: The expected transformation.
    """
    output = create(input_str * num)._pattern
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "input_str, num, expected_output",
    [
        ("test", 2, "test{2}"),
        (CHAR, 2, ".{2}"),
        (WS, (2, 5), r"\s{2,5}"),
        (DIGIT, (0,), r"\d*"),
        (DIGIT, (1,), r"\d+"),
        (DIGIT, (0, 1), r"\d?"),
        (DIGIT, (5,), r"\d{5,}"),
        (DIGIT, (5, 5), r"\d{5}"),
    ],
)
def test_repeat2(input_str, num, expected_output):
    """
    :param input_str: 1st String to transform.
    :param num: multiplier
    :param expected_output: The expected transformation.
    """
    output = create(input_str).repeat(num)._pattern
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "input_str, num, expected_output",
    [
        ("test", -2, pytest.raises(RemagicException)),
        ("test", (9, 2), pytest.raises(RemagicException)),
        ("test", (-2, 8), pytest.raises(RemagicException)),
        ("test", (2, 8, 5), pytest.raises(RemagicException)),
    ],
)
def test_repeat_error(input_str, num, expected_output):
    """
    :param input_str: 1st String to transform.
    :param num: multiplier
    :param expected_output: The expected transformation.
    """
    with expected_output:
        output = create(input_str).repeat(num)._pattern
        assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "func, greedy, expected_output",
    [
        (zero_or_more, True, r"\d*"),
        (one_or_more, True, r"\d+"),
        (zero_or_more, False, r"\d*?"),
        (one_or_more, False, r"\d+?"),
    ],
)
def test_greedy_quantifier(func, greedy, expected_output):
    """
    :param func: function
    :param greedy: bool, True if greedy
    :param expected_output: The expected transformation.
    """
    output = func(DIGIT, greedy=greedy)._pattern
    assert output == expected_output, f"{output} != {expected_output}"
