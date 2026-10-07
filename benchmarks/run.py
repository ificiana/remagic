"""Compare hand-written patterns with remagic output on `re` and `regex`.

Run with `uv run python benchmarks/run.py`; prints a Markdown table of the
best-of-N time per call in milliseconds.
"""

from __future__ import annotations

import random
import re
import timeit
from collections.abc import Callable

import regex

import remagic as rm

random.seed(1)
WORDS = sorted(
    {
        "".join(random.choice("abcdefghij") for _ in range(random.randint(4, 9)))
        for _ in range(300)
    }
)
WORD_TEXT = " ".join(random.choice(WORDS)[: random.randint(3, 9)] for _ in range(4000))
LETTERS = "abcde"

a = rm.exactly("a")
CASES: list[tuple[str, str, rm.Pattern, str]] = [
    ("300 words", "|".join(WORDS), rm.any_of(WORDS), WORD_TEXT),
    (
        "single characters",
        "|".join(LETTERS),
        rm.any_of(LETTERS),
        "xaybzc " * 3000,
    ),
    (
        "(?:ab){20}",
        "(?:ab){20}",
        rm.exactly("ab").times(20),
        "ab" * 19 + "ac " * 3000,
    ),
    (
        "(?:a+)+c on a*22+b",
        "(?:a+)+c",
        a.one_or_more().non_capturing().one_or_more() + "c",
        "a" * 22 + "b",
    ),
    (
        "[a-z]+\\d (already minimal)",
        "[a-z]+\\d",
        rm.char_range("a", "z").one_or_more() + rm.DIGIT,
        "abc 123 " * 3000,
    ),
]


def best(call: Callable[[], object]) -> float:
    """Best-of-seven milliseconds per call, with more loops for fast calls."""
    once = timeit.timeit(call, number=1)
    loops = 1 if once > 0.05 else 10
    return min(timeit.repeat(call, number=loops, repeat=7)) / loops * 1000


def measure(compiled: re.Pattern[str], text: str) -> float:
    """Time `findall` for a compiled pattern."""
    return best(lambda: compiled.findall(text))


def main() -> None:
    """Print the comparison table."""
    print("| Case | re | remagic unoptimized | remagic | regex | remagic on regex |")
    print("|---|---:|---:|---:|---:|---:|")
    for name, hand, built, text in CASES:
        cells = [
            measure(re.compile(hand), text),
            measure(built.compile(optimize=False), text),
            measure(built.compile(), text),
            measure(regex.compile(hand), text),
            measure(built.compile(engine="regex"), text),
        ]
        print(f"| {name} | " + " | ".join(f"{cell:.2f}" for cell in cells) + " |")


if __name__ == "__main__":
    main()
