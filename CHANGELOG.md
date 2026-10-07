# Changelog

## 0.2.0

- Breaking: `Pattern` is immutable; strings combined with patterns are literals.
- Breaking: Python 3.11+ only; `regex` is an optional extra.
- Added `|`, `times`, `between`, `at_least`, lazy and possessive quantifiers,
  `atomic`, named groups, scoped flags, anchors and lookaround methods.
- Fixed `not_before` and `not_after`, the `NOT_NEWLINE` pattern, quantifying
  multi-character patterns and alternations, and the package metadata lookups.
