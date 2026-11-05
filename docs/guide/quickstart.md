# Quickstart

Install with `uv add remagic` (or `pip install remagic`). Python 3.11+ is required.

## Build, compile, match

Start from a building block, combine, then `compile()` to get a compiled
pattern. It is an ordinary `re.Pattern`, or a `regex` pattern with the same
methods when the pattern needs the `regex` engine.

```pycon
>>> import remagic as rm
>>> year = rm.DIGIT.times(4).group("year")
>>> month = rm.DIGIT.times(2).group("month")
>>> date = year + "-" + month
>>> date
Pattern('(?P<year>\\d{4})\\-(?P<month>\\d{2})')
>>> match = date.compile().fullmatch("2027-01")
>>> match["year"], match["month"]
('2027', '01')

```

`str(pattern)` gives the regex source, and `compile(flags)` takes the usual
`re` flags.

## Three rules

1. **Strings are literals.** `"a.b"` matches the text `a.b`, not "a, any
   character, b". Everything you need is built from these pieces; {mod}`remagic.unsafe` exists only as a last resort.
2. **`+` joins, `|` chooses.** Brackets appear only when needed.
3. **Patterns never change.** Every method returns a new pattern, so a pattern
   can be shared and reused safely.

```pycon
>>> str((rm.exactly("cat") | "dog").one_or_more())
'(?:cat|dog)+'

```

## Where next

- {doc}`concepts` explains precedence, quantifiers and the regex engines.
- {doc}`cookbook` has copy-paste recipes.
- {doc}`../api` lists every function and method.
