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


def optional(pattern):
    return Pattern(pattern) * (0, 1)


def zero_or_more(pattern, greedy=True):
    return Pattern(pattern) * (0,) if greedy else optional(Pattern(pattern) * (0,))


def one_or_more(pattern, greedy=True):
    return Pattern(pattern) * (1,) if greedy else optional(Pattern(pattern) * (1,))
