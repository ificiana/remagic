from .constants import Consts
from .pattern import Pattern
from .utils import char_set_escape, escape


def create(pattern):
    if isinstance(pattern, Pattern):
        return pattern
    if isinstance(pattern, Consts):
        return Pattern().create_from_consts(pattern)
    return exactly(pattern)


def exactly(pattern):
    return Pattern(pattern)


def optional(pattern):
    return Pattern(pattern) * (0, 1)


def zero_or_more(pattern, greedy=True):
    return Pattern(pattern) * (0,) if greedy else optional(Pattern(pattern) * (0,))


def one_or_more(pattern, greedy=True):
    return Pattern(pattern) * (1,) if greedy else optional(Pattern(pattern) * (1,))


def _char_set_items(iterable):
    # ordered set of items
    return dict.fromkeys(list("".join([char_set_escape(i) for i in iterable])))


def _alt_items(iterable):
    # ordered set of items
    return dict.fromkeys([escape(i) for i in iterable])


def char_in(iterable):
    return exactly(f"[{''.join(_char_set_items(iterable))}]")


def char_not_in(iterable):
    return exactly(f"[^{''.join(_char_set_items(iterable))}]")


def any_of(iterable):
    return exactly(f"{'|'.join(_alt_items(iterable))}")


def before(pattern):
    return rf"(?={Pattern(pattern)})"


def not_before(pattern):
    return rf"(?!={Pattern(pattern)})"


def after(pattern):
    return rf"(?<={Pattern(pattern)})"


def not_after(pattern):
    return rf"(?<!={Pattern(pattern)})"


def ref(reference):
    if isinstance(reference, int) and reference > 0:
        return rf"\{reference}"
    elif isinstance(reference, str):
        return rf"(?P={reference})"
    return Pattern(reference)
