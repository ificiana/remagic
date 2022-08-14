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
    assert output == expected_output, "{} != {}".format(output, expected_output)


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
    assert output == expected_output, "{} != {}".format(output, expected_output)


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
    assert output == expected_output, "{} != {}".format(output, expected_output)


@pytest.mark.parametrize(
    "input_str, num, expected_output",
    [
        ("test", 2, "testtest"),
        (CHAR, 2, ".{2}"),
    ],
)
def test_multiply_patterns_within_create(input_str, num: int, expected_output):
    """
    :param input_str: 1st String to transform.
    :param num: multiplier
    :param expected_output: The expected transformation.
    """
    output = create(input_str * num)._pattern
    assert output == expected_output, "{} != {}".format(output, expected_output)
