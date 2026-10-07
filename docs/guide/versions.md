# Versions compared

What changed between the releases on PyPI, measured by installing each one and
running the same code. `0.2.0b1`, `0.2.0` and `0.2.1` contain the same library
code, so they appear once as `0.2.1`.

| Version | Date | What it is |
|---|---|---|
| 0.1.0, 0.1.1 | Sep 2022 | Patterns are built as strings. `regex` is a required dependency. |
| 0.1.2a0 | Oct 2022 | Alpha with `ref` and an `exceptions` module. Same string-building design. |
| 0.2.1 | 2026 | Immutable patterns on a syntax tree, an optimizer, `re` by default. |

## Same expression, three versions

Each row builds one expression and checks it against the text it should match.
"Correct" means every check passed.

| Expression | 0.1.1 | 0.1.2a0 | 0.2.1 |
|---|---|---|---|
| `exactly("a.b")` | `a.b`, wrong | `a.b`, wrong | `a\.b`, correct |
| `any_of(["ab", "cd"]) + exactly(",")` | `ab\|cd,`, wrong | `ab\|cd,`, wrong | `(?:ab\|cd),`, correct |
| `one_or_more(exactly("ab"))` | `ab+`, wrong | `ab+`, wrong | `(?:ab)+`, correct |
| `optional(exactly("ab"))` | `ab?`, wrong | `ab?`, wrong | `(?:ab)?`, correct |

The `0.1.x` releases paste text together without escaping it or grouping it, so
a dot matches any character, `|` swallows what follows it, and a quantifier
binds only to the last character. The `0.2` line escapes literals and adds
`(?:...)` where precedence needs it.

## What changed in the API

- Patterns are immutable. `+` joins patterns and `|` alternates them.
- Strings combined with a pattern are literals.
- The `0.1.x` methods `add`, `label` and `repeat` are gone. Use `+`,
  `group("name")` and `times`, `between` or `at_least`.
- New: `char_range`, `non_capturing`, `atomic`, `scoped`, the lookaround
  methods, lazy and possessive quantifiers, `unicode_property`, and the anchors
  `START`, `END`, `WORD_BOUNDARY`.
- `compile()` optimizes the pattern and takes `flags`, `engine` and `optimize`.
  See [](optimization.md).
- `regex` is an optional extra. Patterns compile with `re` unless they need
  `regex`. The `0.1.x` releases always used `regex`.

## Speed

Time per `findall` over 1.5 million characters of Python standard library
source, in milliseconds, best of five. `compile` is the time to build and
compile the pattern from the word list. Python 3.14, one machine.

| Case | 0.1.1 find | 0.1.1 compile | 0.1.2a0 find | 0.1.2a0 compile | 0.2.1 find | 0.2.1 compile |
|---|---:|---:|---:|---:|---:|---:|
| keywords | 247.46 | 0.02 | 305.67 | 0.03 | 66.32 | 1.15 |
| builtin names | 1309.16 | 0.09 | 1328.36 | 0.09 | 131.34 | 8.85 |
| 300 most common identifiers | 1603.10 | 0.16 | 1756.71 | 0.16 | 108.51 | 30.97 |

Searching is 4 to 15 times faster in `0.2.1`. Two things cause that, and the
table does not separate them: `0.1.x` runs on the slower `regex` engine, and
only `0.2.1` merges the alternation into a prefix tree.

The price is compile time. The optimizer takes about 31 ms for 300 words, where
`0.1.x` took 0.16 ms. Compile once and reuse the result.

To reproduce the table, run `uv run python benchmarks/versions.py`. It installs
each version into a throwaway environment, so it needs network access.
