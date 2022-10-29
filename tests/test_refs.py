# flake8: noqa

import pytest

from remagic import *
from remagic.exceptions import RemagicException


@pytest.mark.parametrize(
    "capture, name, expected_output",
    [
        ("captured", "text", "(?P<text>captured)(?P=text)"),
    ],
)
def test_refs(capture, name, expected_output):
    output = create(capture).label("text").ref("text")
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "capture, name, expected_output",
    [
        ("captured", "text", "(?P<text>captured)(?P=text)"),
    ],
)
def test_refs_create(capture, name, expected_output):
    output = create(capture).label("text") + ref("text")
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "capture, expected_output",
    [
        ("captured", r"(captured)\1"),
    ],
)
def test_groups(capture, expected_output):
    output = create(capture).group().ref(1)
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "capture, expected_output",
    [
        ("captured", r"(captured)\1"),
    ],
)
def test_groups_create(capture, expected_output):
    output = create(capture).group() + ref(1)
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "capture, expected_output",
    [
        ("captured", r"(captured)\1"),
    ],
)
def test_groups_create(capture, expected_output):
    output = create(capture).group() + ref(1)
    assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "label, expected_output",
    [
        (["list"], pytest.raises(RemagicException)),
    ],
)
def test_ref_error(label, expected_output):
    with expected_output:
        output = ref(label)
        assert output == expected_output, f"{output} != {expected_output}"


@pytest.mark.parametrize(
    "label, expected_output",
    [
        (["list"], pytest.raises(RemagicException)),
    ],
)
def test_ref_error2(label, expected_output):
    with expected_output:
        output = create("test").ref(label)
        assert output == expected_output, f"{output} != {expected_output}"
