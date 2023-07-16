[![Coverage Status](https://coveralls.io/repos/github/ificiana/remagic/badge.svg?branch=main)](https://coveralls.io/github/ificiana/remagic?branch=main)
![PyPI - Downloads](https://img.shields.io/pypi/dm/remagic)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/remagic)
![PyPI - License](https://img.shields.io/pypi/l/remagic)
[![CodeFactor](https://www.codefactor.io/repository/github/ificiana/remagic/badge)](https://www.codefactor.io/repository/github/ificiana/remagic)

# remagic

Working with regex made easier!
Partly inspired from `magic-regexp` for Node

```py
from remagic import *

pattern1 = create(DIGIT)  # matches any digit
pattern2 = char_in("aeiou")  # matches any char in "aeiou"
pattern3 = ~pattern2  # negates the pattern in pattern2, 
# i.e. match everything except characters in "aeiou"
# Note: remagic 0.1.1 doesn't support the ~ syntax
# use char_not_in("aeiou") instead
pattern4 = pattern1 + pattern3
# finally compile, use standard flags as optional argument
R = pattern4.compile()
# use the regex later
``` 

## Installation

Install from PyPI:
`pip install remagic`

## Work in Progress!

### Documentation

TODO: [docs](https://ificiana.github.io/remagic)

### Known bugs

- improper behaviour with `any_of`
