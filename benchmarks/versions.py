"""Compare released remagic versions on correctness and speed.

Each version is installed by `uv` into a throwaway environment and runs the same
worker code, which uses only calls that exist in every version. Run with
`uv run python benchmarks/versions.py`; prints two Markdown tables.
"""

from __future__ import annotations

import builtins
import collections
import json
import keyword
import re
import subprocess
import sys
import sysconfig
import timeit
from pathlib import Path

VERSIONS = ["0.1.1", "0.1.2a0", "0.2.1"]
PYTHON = "3.14"
CORPUS_LIMIT = 1_500_000

PROBES = [
    ('`exactly("a.b")`', 'rm.exactly("a.b")', [("a.b", True), ("axb", False)]),
    (
        '`any_of(["ab", "cd"]) + exactly(",")`',
        'rm.any_of(["ab", "cd"]) + rm.exactly(",")',
        [("ab,", True), ("cd,", True)],
    ),
    (
        '`one_or_more(exactly("ab"))`',
        'rm.one_or_more(rm.exactly("ab"))',
        [("abab", True), ("ab", True)],
    ),
    (
        '`optional(exactly("ab"))`',
        'rm.optional(rm.exactly("ab"))',
        [("", True), ("ab", True), ("a", False)],
    ),
]


def corpus() -> str:
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


def best(call, loops: int = 1) -> float:
    """Best-of-five milliseconds per call."""
    return min(timeit.repeat(call, number=loops, repeat=5)) / loops * 1000


def worker() -> None:
    """Run inside one remagic version; print its results as JSON."""
    import remagic as rm

    text = corpus()
    top = [
        name
        for name, _ in collections.Counter(
            re.findall(r"[A-Za-z_]\w{3,}", text)
        ).most_common(300)
    ]
    cases = {
        "keywords": keyword.kwlist,
        "builtin names": dir(builtins),
        "300 most common identifiers": top,
    }
    result: dict[str, object] = {"probes": {}, "speed": {}}
    for title, code, checks in PROBES:
        try:
            compiled = eval(code, {"rm": rm}).compile()  # noqa: S307
            source = compiled.pattern
            ok = all(bool(compiled.fullmatch(t)) == want for t, want in checks)
        except Exception as error:
            source, ok = f"{type(error).__name__}", False
        result["probes"][title] = [source, ok]  # type: ignore[index]
    for name, words in cases.items():
        expected = re.findall("|".join(map(re.escape, words)), text)
        compiled = rm.any_of(words).compile()
        assert compiled.findall(text) == expected, name  # noqa: S101
        result["speed"][name] = {  # type: ignore[index]
            "find": best(lambda c=compiled: c.findall(text)),
            "compile": best(lambda w=words: rm.any_of(w).compile()),
        }
    print(json.dumps(result))


def run(version: str) -> dict[str, dict[str, object]]:
    """Run the worker in an environment that has `version` installed."""
    command = [
        "uv", "run", "--no-project", "-p", PYTHON, "--with", f"remagic=={version}",
        "python", "-I", __file__, "--worker",
    ]  # fmt: skip
    done = subprocess.run(command, capture_output=True, text=True, check=True)  # noqa: S603
    return json.loads(done.stdout.splitlines()[-1])


def main() -> None:
    """Print the correctness and speed tables."""
    results = {version: run(version) for version in VERSIONS}
    print("| Expression | " + " | ".join(f"{v} pattern | {v}" for v in VERSIONS) + " |")
    print("|---|" + "---|---|" * len(VERSIONS))
    for title, _, _ in PROBES:
        cells = []
        for version in VERSIONS:
            source, ok = results[version]["probes"][title]  # type: ignore[index]
            cells += [f"`{source}`", "correct" if ok else "wrong"]
        print(f"| {title} | " + " | ".join(cells) + " |")
    print()
    print("| Case | " + " | ".join(f"{v} find | {v} compile" for v in VERSIONS) + " |")
    print("|---|" + "---:|---:|" * len(VERSIONS))
    for name in results[VERSIONS[0]]["speed"]:  # type: ignore[attr-defined]
        cells = []
        for version in VERSIONS:
            row = results[version]["speed"][name]  # type: ignore[index]
            cells += [f"{row['find']:.2f}", f"{row['compile']:.2f}"]
        print(f"| {name} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker()
    else:
        main()
