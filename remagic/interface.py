from .exceptions import RemagicException
from .pattern import Pattern
from .utils import char_set_escape, escape


def create(pattern):
    return pattern if isinstance(pattern, Pattern) else exactly(pattern)


def exactly(pattern):
    return Pattern(pattern)


def optional(pattern):
    return Pattern(pattern) * (0, 1)


def zero_or_more(pattern, greedy=True):
    if greedy:
        return Pattern(pattern) * (0,)
    return optional(Pattern(pattern) * (0,))


def one_or_more(pattern, greedy=True):
    if greedy:
        return Pattern(pattern) * (1,)
    return optional(Pattern(pattern) * (1,))


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


# TODO: Write tests for `before`, `not_before`, `after`, `not_after`


def before(pattern):  # pragma: no cover
    return rf"(?={create(pattern)})"


def not_before(pattern):  # pragma: no cover
    return rf"(?!={create(pattern)})"


def after(pattern):  # pragma: no cover
    return rf"(?<={create(pattern)})"


def not_after(pattern):  # pragma: no cover
    return rf"(?<!={create(pattern)})"


def ref(reference):
    if isinstance(reference, int) and reference > 0:
        return exactly(rf"\{reference}")
    if isinstance(reference, str):
        return exactly(rf"(?P={reference})")
    raise RemagicException("Only positive integers and strings are allowed")
