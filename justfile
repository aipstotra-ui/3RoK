# Shortcut menu. Run `just` to list recipes, `just verify` before every commit.

default:
    @just --list

# Install all Python and TypeScript dependencies
setup:
    uv sync
    pnpm install

# Run every check: style, types, tests, build (Python + TypeScript)
verify: verify-py verify-ts

verify-py:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy packages/py/orbitlife/src packages/py/orbitlife-build/src
    uv run pytest

verify-ts:
    pnpm lint
    pnpm typecheck
    pnpm test
    pnpm build

# Auto-fix formatting in both languages
fmt:
    uv run ruff format .
    uv run ruff check --fix .
    pnpm exec biome check --write .
