# Benchmarks

Each row finds every match of one pattern in 1,570,959 characters of real
code, the Python standard library's own `.py` files. The pattern is written by
hand and built with remagic, on the standard `re` module and on `regex`. Before
timing, the script checks that remagic finds exactly the same matches as the
hand-written pattern. Times are milliseconds per `findall` call, best of seven,
so lower is better; "vs" columns are remagic divided by hand-written, so below
1× means remagic is faster and above 1× means it is slower.

| Case | re | remagic unoptimized | remagic | vs re | regex | remagic on regex | vs regex | same pattern on re |
|---|---:|---:|---:|---:|---:|---:|---:|:-:|
| keywords | 230.92 | 114.89 | 72.93 | 0.32× | 285.92 | 283.07 | 0.99× | no |
| keywords with word boundaries | 73.22 | 75.04 | 52.96 | 0.72× | 96.89 | 95.85 | 0.99× | no |
| builtin names | 397.61 | 415.82 | 131.29 | 0.33× | 1603.75 | 708.86 | 0.44× | no |
| 300 most common identifiers | 564.20 | 601.25 | 127.47 | 0.23× | 1963.74 | 508.17 | 0.26× | no |
| identifier | 58.63 | 69.37 | 47.93 | 0.82× | 87.28 | 73.26 | 0.84× | no |
| number with optional fraction | 35.96 | 36.37 | 39.24 | 1.09× | 11.26 | 11.29 | 1.00× | no |
| hex literal | 0.69 | 0.64 | 0.65 | 0.93× | 0.89 | 0.90 | 1.00× | no |
| double-quoted string | 2.97 | 3.11 | 3.02 | 1.02× | 4.12 | 4.35 | 1.06× | no |
| comment | 1.69 | 1.68 | 1.69 | 1.00× | 2.34 | 2.33 | 1.00× | no |
| function definition | 3.85 | 3.94 | 3.92 | 1.02× | 3.20 | 2.93 | 0.92× | no |
| trailing whitespace | 65.97 | 71.38 | 70.62 | 1.07× | 102.28 | 104.12 | 1.02× | no |
| lowercase word then space | 82.88 | 88.08 | 68.01 | 0.82× | 137.48 | 131.63 | 0.96× | no |
| word then comma | 101.12 | 96.54 | 88.70 | 0.88× | 178.62 | 182.39 | 1.02× | no |
| four-digit year | 37.08 | 36.95 | 36.24 | 0.98× | 8.93 | 8.95 | 1.00× | yes |

- **remagic unoptimized** is `compile(optimize=False)`: the pattern as built.
- **remagic** is the default `compile()`, on `re`.
- **remagic on regex** is `compile(engine="regex")`.
- **same pattern on re** says whether remagic produced the same source as the
  hand-written pattern.

## Reading the table

- **Large alternations win.** `any_of` over the 300 most common identifiers
  runs about 4× faster than the hand-written `a|b|…` on both engines, and the
  builtin names about 3× on `re` and 2.3× on `regex`. The 35 keywords gain 3×
  on `re` in this run and nothing on `regex`.
- **Everything else is a tie.** Rows where remagic is within about ±10% of the
  hand-written pattern are noise: repeated runs of the identical pattern
  varied by that much, and rows such as the four-digit year (the same pattern,
  0.98×) show it. Some rows read slightly above 1× (the number pattern at 1.09×
  on `re`, trailing whitespace at 1.07×); we found no case that is reliably
  slower, but we cannot rule out a small cost.
- **The possessive rewrite is a small gain, not a rescue.** Patterns like
  `[a-z]+\s` and `\w+,` ran 10–20% faster on `re`; on `regex` the rewrite is
  skipped because it ran slower there.
- **Short, simple patterns are the same.** The identifier, hex, string and
  comment patterns are already minimal, so remagic has nothing to remove.

## A synthetic worst case

Real code rarely triggers catastrophic backtracking, so this one is
synthetic: `(?:a+)+c` against twenty-two `a` characters followed by `b`. It is
here to show the failure mode that remagic removes, not as typical behavior.

| Case | re | remagic | regex | remagic on regex |
|---|---:|---:|---:|---:|
| `(?:a+)+c` on `a`×22 + `b` | 361.11 | 0.00 | 0.14 | 0.00 |

## Running them yourself

```sh
uv run python benchmarks/run.py
```

The numbers depend on the machine and Python version (these ran on Python
3.14), and the corpus is the standard library of whichever Python runs the
script, so treat them as relative, not absolute.
