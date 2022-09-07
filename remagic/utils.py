import re


def escape(string):
    S_CHAR = r"([\.\+\*\?\^\$\(\)\[\]\{\}\|\\])"
    return re.sub(S_CHAR, r"\\\1", str(string))


def char_set_escape(string):
    S_CHAR = r"([\^\-\]\\])"
    return re.sub(S_CHAR, r"\\\1", str(string))
