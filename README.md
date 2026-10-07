[![build](https://github.com/ificiana/remagic/actions/workflows/build.yml/badge.svg)](https://github.com/ificiana/remagic/actions/workflows/build.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/remagic)
![PyPI - License](https://img.shields.io/pypi/l/remagic)

<p align="center"><img src="assets/logo.svg" alt="remagic logo" width="96"></p>

# remagic

Build regular expressions from composable, typed Python objects. Partly inspired
by `magic-regexp` for Node.

```pycon
>>> import remagic as rm
>>> year = rm.DIGIT.times(4).group("year")
>>> month = rm.DIGIT.times(2).group("month")
>>> date = rm.START + year + "-" + month + rm.END
>>> date.compile().fullmatch("2027-01")["year"]
'2027'

```

Patterns are immutable. Strings are matched literally, `+` concatenates, `|`
alternates, and `(?:...)` is added only where precedence needs it:

```pycon
>>> str((rm.exactly("a") | "b").times(2))
'(?:a|b){2}'

```

## Installation

```sh
uv add remagic            # or: pip install remagic
uv add "remagic[regex]"   # optional: the `regex` engine
```

Requires Python 3.11+. Patterns compile with the standard `re` module. Features
that only `regex` supports, such as `unicode_property("L")`, switch to it
automatically and need the `regex` extra.

## Learn more

See the [quickstart](https://ificiana.github.io/remagic/guide/quickstart.html), [concepts](https://ificiana.github.io/remagic/guide/concepts.html) and
[cookbook](https://ificiana.github.io/remagic/guide/cookbook.html) in the docs, or the building blocks below.

## Building blocks

- Constants: `DIGIT`, `WORD`, `WHITESPACE`, `LETTER`, `CHAR`, `NEWLINE`, ... and
  anchors `START`, `END`, `WORD_BOUNDARY`, ...
- Characters: `exactly`, `char_in`, `char_not_in`, `char_range`, `any_of`,
  `unicode_property`
- Quantifiers: `optional`, `zero_or_more`, `one_or_more`, `times`, `between`,
  `at_least`, each with `lazy=` and `possessive=`
- Groups: `group` (numbered or named), `non_capturing`, `atomic`, `ref`
- Assertions: `before`, `not_before`, `after`, `not_after`, and the methods
  `followed_by`, `not_followed_by`, `preceded_by`, `not_preceded_by`
- Flags: `scoped`, `ignore_case`, `multiline`, `dotall`
- Every function has a matching `Pattern` method.

## Development

```sh
uv sync
uv run pytest        # 100% line and branch coverage is required
uv run ruff check . && uv run ruff format --check . && uv run mypy
uv run --group docs sphinx-build -W -b html docs docs/_build   # build the docs
```
