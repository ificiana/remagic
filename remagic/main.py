"""
This module contains logic for Pattern creation.
"""

from .pattern import Pattern, exactly


def create(pattern=None) -> Pattern:
    """
    Create patterns from regex strings or other Pattern objects
    :param pattern: String or Pattern
    :return: Pattern object
    """
    if pattern is None:
        return Pattern()
    if isinstance(pattern, Pattern):
        return pattern
    return exactly(pattern)
