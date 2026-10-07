# Benchmarks

Patterns that look alike can run very differently. Each row compares the same
pattern written by hand and built with remagic, on the standard `re` module and
on `regex`. Times are milliseconds per `findall` call, best of seven, so lower
is better.

| Case | re | remagic unoptimized | remagic | regex | remagic on regex |
|---|---:|---:|---:|---:|---:|
| 300 words | 10.32 | 10.62 | 1.66 | 32.72 | 5.93 |
| single characters | 1.31 | 1.58 | 1.59 | 2.68 | 2.65 |
| (?:ab){20} | 0.48 | 0.46 | 0.02 | 0.02 | 0.00 |
| (?:a+)+c on a*22+b | 361.11 | 409.92 | 0.00 | 0.14 | 0.00 |
| [a-z]+\d (already minimal) | 1.01 | 0.99 | 0.70 | 1.19 | 1.22 |

- **remagic unoptimized** is `compile(optimize=False)`: the pattern as built.
- **remagic** is the default `compile()`, on `re`.
- **remagic on regex** is `compile(engine="regex")`.

## Reading the table

- **Many alternatives:** `any_of` over 300 words is factored into a prefix tree,
  about six times faster on `re` and `regex`.
- **Single characters:** `a|b|c|d|e` already compiles to the same work as
  `[a-e]` on both engines, so nothing changes.
- **Exact repeats of a short literal:** `(?:ab){20}` becomes `abab…`, which the
  engines match far faster than a repeat.
- **Nested quantifiers:** `(?:a+)+c` backtracks exponentially when written by
  hand; remagic rewrites it to a pattern that fails in linear time. `regex`
  copes on its own here.
- **Already minimal:** `[a-z]+\d` is unchanged on `regex`; on `re` the possessive
  rewrite is a modest gain.

## Running them yourself

```sh
uv run python benchmarks/run.py
```

The numbers depend on the machine, the Python version and the input text, so
treat them as relative, not absolute. They were measured on Python 3.14 with
synthetic text.
