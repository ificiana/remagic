from .constants import Consts
from .pattern import Pattern


def create(pattern):
    if isinstance(pattern, Pattern):
        return pattern
    if isinstance(pattern, Consts):
        return Pattern().create(pattern)
    return exactly(pattern)


def exactly(pattern):
    return Pattern(pattern)
