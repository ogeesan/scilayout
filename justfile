# List available recipes
default:
    @just --list

# Install/sync dev dependencies
sync:
    uv sync

# Format code
format:
    uv run ruff format .
    uv run ruff check --select I --fix .

# Lint (no changes)
lint:
    uv run ruff check .
    uv run ruff format --check .

# Lint and apply safe auto-fixes
fix:
    uv run ruff check --fix .

# Type check
typecheck:
    uv run pyright

# Run tests
test *args:
    uv run pytest {{args}}

# Run tests with coverage
cov:
    uv run pytest --cov=scilayout --cov-report=term-missing

# Lint, type check and tests
check: lint typecheck test

# Serve docs locally
docs:
    uv run mkdocs serve

# Build docs
docs-build:
    uv run mkdocs build --strict

# Build sdist and wheel
build:
    uv build

# Remove build and cache artefacts
clean:
    rm -rf build dist site .pytest_cache .ruff_cache .coverage
    find . -name __pycache__ -type d -prune -not -path "./.venv/*" -exec rm -rf {} +
