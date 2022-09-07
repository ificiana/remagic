# flake8: noqa

import pytest

from remagic import *


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
    assert output._pattern == expected_output, "{} != {}".format(
        output, expected_output
    )
