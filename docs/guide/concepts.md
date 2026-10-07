# Concepts

## Functions and methods

Every builder exists twice: as a method on `Pattern` and as a function that
accepts a pattern or a string. These are equal:

```pycon
>>> import remagic as rm
>>> rm.exactly("ab").optional() == rm.optional("ab")
True

```

Use whichever reads better. Methods chain; functions are handy for the first step.

## Precedence

A pattern remembers how tightly it binds, so combining never changes the meaning.

```pycon
>>> str(rm.exactly("ab").times(2))
'(?:ab){2}'
>>> str(rm.exactly("a").times(2))
'a{2}'
>>> str(rm.exactly("a").one_or_more().one_or_more())
'(?:a+)+'

```

That last line matters: writing `a++` by hand would be a possessive quantifier,
not a repeated one.

## Quantifiers

| Method | Matches |
| --- | --- |
| `optional()` | 0 or 1 |
| `zero_or_more()` | 0 or more |
| `one_or_more()` | 1 or more |
| `times(n)` | exactly `n` |
| `between(low, high)` | `low` to `high` |
| `at_least(n)` | `n` or more |

Each takes `lazy=True` (as few as possible) or `possessive=True` (never give
back); the two cannot be combined.

```pycon
>>> str(rm.CHAR.zero_or_more(lazy=True))
'.*?'

```

## Groups and references

`group()` captures, `group("name")` captures under a name, and
`non_capturing()` only groups. `ref(1)` or `ref("name")` matches the same text
again.

```pycon
>>> doubled = rm.WORD.one_or_more().group("w") + " " + rm.ref("w")
>>> bool(doubled.compile().fullmatch("hello hello"))
True
>>> bool(doubled.compile().fullmatch("hello world"))
False

```

## Assertions

Lookarounds check the surroundings without consuming them. As methods they read
naturally:

```pycon
>>> price = rm.DIGIT.one_or_more().preceded_by("$")
>>> price.compile().search("cost: $42").group()
'42'

```

Anchors are constants: `START`, `END`, `START_OF_STRING`, `END_OF_STRING`,
`WORD_BOUNDARY` and `NOT_WORD_BOUNDARY`.

## Flags

Flags apply to one part of a pattern, using Python's inline syntax:

```pycon
>>> str(rm.exactly("abc").ignore_case())
'(?i:abc)'
>>> str(rm.exactly("abc").scoped(on="i", off="s"))
'(?i-s:abc)'

```

## Engines

Patterns compile with the standard `re` module. Features only the third-party
`regex` module offers, such as `unicode_property("L")`, mark the pattern so that
`compile()` uses `regex` automatically. Install it with `remagic[regex]`; if it
is missing, `compile()` raises {class}`~remagic.RemagicException` telling you so.
Force an engine with `compile(engine="re")` or `compile(engine="regex")`.

## Errors

Invalid input raises {class}`~remagic.RemagicException`, a `ValueError`, with a
message naming the problem. Passing the wrong type (for example a number where
text is expected) raises `TypeError`.
