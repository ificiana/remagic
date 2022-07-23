import pytest

import remagic
from remagic import *


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("test", "test"),
        (CHAR, "."),
        (".", "."),
        (r"a sentence\.", r"a sentence\."),
        (r"another " + r"sentence\.", r"another sentence\."),
        (create(r"vowel: ") + char_in("aeiou"), r"vowel: [aeiou]"),
    ],
)
def test_create_pattern(input_str, expected_output):
    """
    :param input_str: String that will be transformed.
    :param expected_output: The expected transformation.
    """
    output = remagic.create(input_str).regex
    assert output == expected_output, "{} != {}".format(
        output, expected_output
    )
