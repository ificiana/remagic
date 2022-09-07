import re

SPECIALS = re.compile(r"([.+*?^$()\[\]{}|\\])")
CLASS_SPECIALS = re.compile(r"([\^\-\]\\])")


def escape(string):
    return SPECIALS.sub(r"\\\1", str(string))


def char_set_escape(string):
    return CLASS_SPECIALS.sub(r"\\\1", str(string))
