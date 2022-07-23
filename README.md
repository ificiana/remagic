[![Coverage Status](https://coveralls.io/repos/github/ificiana/remagic/badge.svg?branch=main)](https://coveralls.io/github/ificiana/remagic?branch=main)

# remagic
Working with regex made easier! 
Partly inspired from `magic-regexp` for Node

```py
from remagic import *
pattern1 = create(DIGIT)  # matches any digit
pattern2 = char_in("aeiou")  # matches any char in "aeiou"
pattern3 = ~pattern2  # negates the pattern in pattern2, 
# i.e. match everything except characters in "aeiou"
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
