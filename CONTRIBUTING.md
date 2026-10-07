# How to contribute

## Setup

Dependencies are managed with [`uv`](https://docs.astral.sh/uv/):

```bash
uv sync
uv run pre-commit install
```

## Checks

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
```

`pytest` fails below 100% line and branch coverage.

## Before submitting

1. Write a failing test first, then the change.
2. Update the README or docs if behaviour changes.
3. Run the checks above.
4. Use [Conventional Commits](https://www.conventionalcommits.org/) messages (`feat:`, `fix:`, `docs:`, ...).

## Other help

You can also contribute by spreading the word about this library or writing a
short article on how you use it.
