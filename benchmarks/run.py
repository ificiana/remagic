"""Compare hand-written patterns with remagic output on real source code.

The corpus is the standard library's own `.py` files, so every machine runs the
same kind of text. Each remagic pattern is checked to find exactly what the
hand-written one finds before it is timed.

Run with `uv run python benchmarks/run.py`; prints Markdown tables of the
best-of-seven time per `findall` call in milliseconds.
"""

from __future__ import annotations

import builtins
import collections
import keyword
import re
import sysconfig
import timeit
from collections.abc import Callable
from pathlib import Path

import regex

import remagic as rm

CORPUS_LIMIT = 1_500_000


def load_corpus() -> str:
    """Concatenate the standard library's top-level modules, up to a size cap."""
    root = Path(sysconfig.get_paths()["stdlib"])
    chunks: list[str] = []
    size = 0
    for path in sorted(root.glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        chunks.append(text)
        size += len(text)
        if size >= CORPUS_LIMIT:
            break
    return "".join(chunks)


TEXT = load_corpus()
IDENTIFIER = rm.char_in("_", ranges=[("a", "z"), ("A", "Z")]) + rm.WORD.zero_or_more()
TOP_NAMES = [
    name
    for name, _ in collections.Counter(
        re.findall(r"[A-Za-z_]\w{3,}", TEXT)
    ).most_common(300)
]
HEX = rm.char_in("", ranges=[("0", "9"), ("a", "f"), ("A", "F")])
Case = tuple[str, str, rm.Pattern, int]
CASES: list[Case] = [
    (
        "keywords",
        "|".join(keyword.kwlist),
        rm.any_of(keyword.kwlist),
        0,
    ),
    (
        "keywords with word boundaries",
        r"\b(?:" + "|".join(keyword.kwlist) + r")\b",
        rm.WORD_BOUNDARY + rm.any_of(keyword.kwlist).non_capturing() + rm.WORD_BOUNDARY,
        0,
    ),
    (
        "builtin names",
        "|".join(dir(builtins)),
        rm.any_of(dir(builtins)),
        0,
    ),
    (
        "300 most common identifiers",
        "|".join(TOP_NAMES),
        rm.any_of(TOP_NAMES),
        0,
    ),
    ("identifier", r"[a-zA-Z_]\w*", IDENTIFIER, 0),
    (
        "number with optional fraction",
        r"\d+(?:\.\d+)?",
        rm.DIGIT.one_or_more() + (rm.exactly(".") + rm.DIGIT.one_or_more()).optional(),
        0,
    ),
    (
        "hex literal",
        r"0[xX][0-9a-fA-F]+",
        rm.exactly("0") + rm.char_in("xX") + HEX.one_or_more(),
        0,
    ),
    (
        "double-quoted string",
        r'"[^"\n]*"',
        rm.exactly('"') + rm.char_not_in('"\n').zero_or_more() + '"',
        0,
    ),
    (
        "comment",
        r"#.*",
        rm.exactly("#") + rm.CHAR.zero_or_more(),
        0,
    ),
    (
        "function definition",
        r"def\s+(\w+)\s*\(",
        rm.exactly("def")
        + rm.WS.one_or_more()
        + rm.WORD.one_or_more().group()
        + rm.WS.zero_or_more()
        + "(",
        0,
    ),
    (
        "trailing whitespace",
        r"[ \t]+$",
        rm.char_in(" \t").one_or_more() + rm.END,
        re.MULTILINE,
    ),
    (
        "lowercase word then space",
        r"[a-z]+\s",
        rm.char_range("a", "z").one_or_more() + rm.WS,
        0,
    ),
    (
        "word then comma",
        r"\w+,",
        rm.WORD.one_or_more() + ",",
        0,
    ),
    (
        "four-digit year",
        r"\b\d{4}\b",
        rm.WORD_BOUNDARY + rm.DIGIT.times(4) + rm.WORD_BOUNDARY,
        0,
    ),
]


def best(call: Callable[[], object]) -> float:
    """Best-of-seven milliseconds per call, with more loops for fast calls."""
    once = timeit.timeit(call, number=1)
    loops = 1 if once > 0.05 else 10
    return min(timeit.repeat(call, number=loops, repeat=7)) / loops * 1000


def measure(compiled: re.Pattern[str]) -> float:
    """Time `findall` over the corpus."""
    return best(lambda: compiled.findall(TEXT))


def main() -> None:
    """Print the comparison table."""
    print(f"Corpus: {len(TEXT):,} characters of standard library source.\n")
    print(
        "| Case | re | remagic unoptimized | remagic | vs re | regex "
        "| remagic on regex | vs regex | same pattern on re |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---:|:-:|")
    for name, hand, built, flags in CASES:
        expected = re.compile(hand, flags).findall(TEXT)
        for engine in ("re", "regex"):
            assert built.compile(flags, engine=engine).findall(TEXT) == expected, name  # type: ignore[arg-type]  # noqa: S101
        times = [
            measure(re.compile(hand, flags)),
            measure(built.compile(flags, optimize=False)),
            measure(built.compile(flags)),
            measure(regex.compile(hand, flags)),
            measure(built.compile(flags, engine="regex")),
        ]
        row = [
            f"{times[0]:.2f}",
            f"{times[1]:.2f}",
            f"{times[2]:.2f}",
            f"{times[2] / times[0]:.2f}\u00d7",
            f"{times[3]:.2f}",
            f"{times[4]:.2f}",
            f"{times[4] / times[3]:.2f}\u00d7",
        ]
        same = "yes" if built.compile(flags).pattern == hand else "no"
        print(f"| {name} | " + " | ".join([*row, same]) + " |")


if __name__ == "__main__":
    main()
