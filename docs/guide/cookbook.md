# Cookbook

```pycon
>>> import remagic as rm

```

## ISO date

```pycon
>>> day = rm.DIGIT.times(2)
>>> iso = rm.START + rm.DIGIT.times(4) + "-" + day + "-" + day + rm.END
>>> bool(iso.compile().match("2027-03-14"))
True

```

## Hex colour

```pycon
>>> hexdigit = rm.char_in("", ranges=[("0", "9"), ("a", "f"), ("A", "F")])
>>> colour = "#" + (hexdigit.times(6) | hexdigit.times(3))
>>> [bool(colour.compile().fullmatch(s)) for s in ("#fff", "#a1b2c3", "#ffff")]
[True, True, False]

```

## Semantic version

```pycon
>>> number = rm.DIGIT.one_or_more()
>>> core = number.group("major") + "." + number.group("minor") + "." + number.group("patch")
>>> m = core.compile().fullmatch("1.20.3")
>>> m["major"], m["minor"], m["patch"]
('1', '20', '3')

```

## Repeated words

```pycon
>>> repeat = (
...     rm.WORD_BOUNDARY + rm.WORD.one_or_more().group("w") + rm.WHITESPACE + rm.ref("w")
... )
>>> repeat.compile().search("this is is a test").group("w")
'is'

```

## Words that are not followed by something

```pycon
>>> rm.exactly("foo").not_followed_by("bar").compile().findall("foobar foobaz")
['foo']

```

## Case-insensitive part of a pattern

```pycon
>>> tag = "ID-" + rm.char_in("", ranges=[("a", "z")]).times(3).ignore_case()
>>> bool(tag.compile().fullmatch("ID-AbC"))
True
>>> bool(tag.compile().fullmatch("id-abc"))
False

```

## Any word from a list

`any_of` escapes each item and removes duplicates.

```pycon
>>> keywords = rm.any_of(["if", "else", "c++"])
>>> [m.group() for m in (rm.WORD_BOUNDARY + keywords).compile().finditer("if c++ else")]
['if', 'c++', 'else']

```

## Letters in any script

Needs the `regex` extra.

```pycon
>>> word = rm.unicode_property("L").one_or_more()
>>> word.compile().findall("naïve façade")
['naïve', 'façade']

```
