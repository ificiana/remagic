"""Escape hatch for regex source that remagic cannot build.

Patterns made here are opaque: remagic cannot check or optimize them, and
mistakes surface only when the engine compiles the result. Prefer the builders
in `remagic` and reach for this module only when nothing there fits.
"""

from __future__ import annotations

from . import _tree as tree
from .pattern import Pattern


def raw(source: str, *, needs_regex: bool = False) -> Pattern:
    """Wrap existing regex source, treated as lowest precedence.

    Example:
        >>> from remagic import unsafe
        >>> str(unsafe.raw("a|b") + "c")
        '(?:a|b)c'
    """
    return Pattern(tree.Raw(source, tree.Precedence.ALTERNATION, needs_regex))
