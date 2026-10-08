# remagic

Python library that builds regular expressions from immutable, composable objects.
Default branch is `dev`. Supports Python 3.11+; `regex` is an optional extra.

## Commands

Use `uv`, never pip or bare `python`.

```sh
uv sync
uv run pytest                 # doctests in src, docs and README; fails under 100% line+branch coverage
uv run ruff format . && uv run ruff check . && uv run mypy
uv run --group docs sphinx-build -W -b html docs docs/_build
uv run python benchmarks/run.py        # ~5 min, real-code benchmark table
uv run python benchmarks/versions.py   # installs old releases from PyPI, needs network
```

## Architecture

- `src/remagic/_tree.py`: the immutable syntax tree (`Lit`, `CharSet`, `Seq`, `Alt`, `Repeat`,
  `Group`, `Look`, `Raw`, ...), `render`, and the optimizer (`optimize`).
- `src/remagic/pattern.py`: `Pattern` wraps one tree node. `source`, `precedence` and
  `needs_regex` are derived from it. `compile()` optimizes, then picks `re` or `regex`.
- `src/remagic/interface.py` and `constants.py`: the public functions and constants; they build
  `Pattern(tree.…)`.
- `src/remagic/unsafe.py`: `raw()`, an opaque escape hatch. Raw nodes disable the possessive and
  reorder rewrites and are assumed to possibly capture.
- The optimizer has two levels. `"safe"` (default) must keep identical match spans and groups.
  `"aggressive"` may reorder alternatives and is valid only for fullmatch or boolean use.
  Possessive rewriting is skipped on the `regex` engine because it is slower there.

## Rules for changes

- Test first. Every bug gets a regression test. Coverage must stay at 100% and must not depend
  on Hypothesis luck: add a deterministic test for every optimizer branch.
- Any optimizer rewrite needs the differential tests in `tests/test_optimize.py` to pass and a
  benchmark that justifies it. Do not add rewrites that are not provably equivalent.
- Capturing groups are always kept. Treat `Raw` as possibly capturing (`tree.may_capture`).
- Docs describe what is, never what was. Only short "Pitfall" notes mention history. The docs
  build is `-W` and `nitpicky`, so cross-references must resolve.
- Benchmark tables in `docs/guide/` are pasted from the scripts and refreshed by hand.
- Conventional Commits. Stage files by explicit path.
