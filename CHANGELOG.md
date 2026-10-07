# Changelog

## 0.2.1

- The README logo uses an absolute URL so it renders on PyPI.
- The docs workflow deploys from `dev`.

## 0.2.0

- Breaking: `Pattern` is immutable; strings combined with patterns are literals.
- Breaking: Python 3.11+ only; `regex` is an optional extra.
- `compile()` optimizes patterns (`optimize=True`, `"aggressive"` or `False`); `Pattern.optimized()` shows the result.
- Breaking: `raw` moved to `remagic.unsafe.raw`; raw patterns are never optimized.
- Added `|`, `times`, `between`, `at_least`, lazy and possessive quantifiers,
  `atomic`, named groups, scoped flags, anchors and lookaround methods.
- Fixed `not_before` and `not_after`, the `NOT_NEWLINE` pattern, quantifying
  multi-character patterns and alternations, and the package metadata lookups.
- The optimizer collapses `x|x?` to `x?`, which removes exponential backtracking in
  patterns such as `(a|a?)+c`.
