# flake8: noqa

import pytest

from remagic import *


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
