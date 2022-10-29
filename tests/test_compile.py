# flake8: noqa

import warnings

import pytest

try:
    import regex as re
except ImportError:
    import re  # type: ignore[no-redef]

    warnings.warn(
        "`regex` module not found," " using builtin `re` module", ImportWarning
    )

from remagic import *


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("test", "test"),
        (".", "."),
        (r"a sentence\.", r"a sentence\."),
        (CHAR, "."),
        (CHAR + N, r".\n"),
        (WS * 5, r"\s{5}"),
        (WS * (1, 3), r"\s{1,3}"),
        (8, "8"),
    ],
)
def test_compile_pattern(input_str, expected_output):
    """
    :param input_str: Pattern to compile in remagic.
    :param expected_output: Pattern to compile in regex or re.
    """
    output = create(input_str).compile()
    assert output == re.compile(expected_output), f"{output} != {expected_output}"
