"""
This module contains utility functions.
"""

import regex


def class_escape(iterable):
    """
    Function for escaping additional characters within a regex character class
    :param iterable: An Iterable object
    :return: RegEx string
    """
    res = ""
    pat_ = regex.compile(r"[-\\^\]]")
    for i in iterable:
        res += pat_.sub(r"\g<0>", regex.escape(i))
    return res
