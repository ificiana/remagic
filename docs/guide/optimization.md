# Optimization

`compile()` rewrites a pattern into a cheaper one before handing it to the
engine. `str(pattern)` always shows the pattern as built; `optimized()` shows
what `compile()` uses.

```pycon
>>> import remagic as rm
>>> pattern = rm.any_of("abc").one_or_more().non_capturing().one_or_more()
>>> str(pattern)
'(?:(?:a|b|c)+)+'
>>> str(pattern.optimized())
'[abc]++'

```

## Safe level (default)

The safe level only applies rewrites that keep every match, span and group
identical. It merges adjacent literals, characters and repeats, collapses
nested quantifiers, drops redundant groups, merges single-character
alternatives into a class, and turns a greedy repeat possessive when the text
after it can never start with a character it matches. That removes
catastrophic backtracking such as `(?:a+)+c` against `aaaa…b`.

```pycon
>>> str((rm.exactly("a") | "b" | "c").optimized())
'[abc]'
>>> str(rm.exactly("a").times(2).non_capturing().times(3).optimized())
'a{6}'
>>> str((rm.DIGIT.one_or_more() + "x").optimized())
'\\d++x'

```

Capturing groups are kept, so group numbers never shift. `unsafe.raw()` patterns and
scoped flags are opaque, and flags such as `re.IGNORECASE` also disable the
rewrites that depend on knowing exactly which characters match.

## Aggressive level

`optimize="aggressive"` also factors common prefixes and reorders alternatives.
That can change which match is found first, so use it with `fullmatch` or
yes/no checks only.

```pycon
>>> pattern = rm.exactly("foobar") | "foobaz"
>>> str(pattern.optimized("aggressive"))
'fooba[rz]'
>>> pattern.compile(optimize="aggressive").fullmatch("foobaz") is not None
True

```

## Turning it off

```pycon
>>> rm.exactly("a").compile(optimize=False).pattern
'a'

```
