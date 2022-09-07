from .constants import Consts
from .pattern import Pattern
from .utils import char_set_escape, escape


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


def char_in(iterable):
    f = [char_set_escape(i) for i in iterable]
    return exactly(f"[{''.join(f)}]")


def char_not_in(iterable):
    f = [char_set_escape(i) for i in iterable]
    return exactly(f"[^{''.join(f)}]")


def any_of(iterable):
    f = [escape(i) for i in iterable]
    return exactly(f"[{'|'.join(f)}]")
