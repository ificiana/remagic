from remagic import *


def test_version():
    """
    Test the version
    """
    output = version
    assert output != "unknown", "Version check failed"


def test_version_function():
    """
    Test the version
    """
    output = get_version()
    assert output != "unknown", "Version check failed"
