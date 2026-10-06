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

# Download a data release from GitHub and check every sha256 (ADR 0005). Example: just data-verify data-v0
data-verify release:
    rm -rf data-cache/{{release}}
    gh release download {{release}} -D data-cache/{{release}}
    uv run python -m orbitlife_build.manifest verify data-cache/{{release}}/manifest.json data-cache/{{release}}

# Run the scientific validation suite (validation/cases). Add --strict to also fail on
# NOT_IMPLEMENTED cases and on matches against UNVERIFIED references (required from Phase 2 exit).
validate *args:
    uv run python -m orbitlife_build.validation {{args}}
