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

# Run the visual tests and keep their SVG/PNG output in test_outputs/ to look at
visual:
    uv run pytest -m visual --keep-outputs -q
    @echo "Files in test_outputs/ ready for inspection."

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
    uv run zensical serve

# Build docs, failing on warnings and on unresolved cross-references
docs-build:
    uv run zensical build --strict --clean
    uv run python scripts/check_site.py

# Build sdist and wheel
build:
    uv build

# Remove build and cache artefacts
clean:
    rm -rf build dist site .pytest_cache .ruff_cache .coverage
    find . -name __pycache__ -type d -prune -not -path "./.venv/*" -exec rm -rf {} +
