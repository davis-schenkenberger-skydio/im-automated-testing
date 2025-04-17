[private]
default:
    @just -l

test *args:
    uv run pytest -vs {{args}}

trace file:
    uv run playwright show-trace {{file}}

flake *args:
    uv run pytest -vs --tracing=on --flake-finder {{args}}

fmt:
    uv run ruff check --fix
    uv run ruff format