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

# Sanity check: run the tests against a spread of matplotlib versions (needs network, ~1 minute)
compat:
    #!/usr/bin/env bash
    set -u
    failed=0
    # matplotlib before 3.9 needs numpy 1.x
    for spec in "3.5.0 numpy==1.21.3" "3.5.3 numpy<2" "3.6.3 numpy<2" "3.7.5 numpy<2" "3.8.4 numpy<2" "3.9.4" "3.10.5" "latest"; do
        mpl=${spec%% *}
        np=""
        [[ "$spec" == *" "* ]] && np=${spec#* }
        # uv.lock only covers Python 3.11+, so skip the project and its lockfile
        args=(--isolated --no-project --python 3.10 --with-editable . --with pytest --with defusedxml)
        if [[ "$mpl" == latest ]]; then args+=(--with matplotlib --upgrade); else args+=(--with "matplotlib==$mpl"); fi
        [[ -n "$np" ]] && args+=(--with "$np")
        printf '%-36s' "matplotlib $mpl ${np:+($np)}"
        if out=$(MPLBACKEND=Agg uv run "${args[@]}" pytest -q -p no:cacheprovider 2>&1); then
            echo "$(echo "$out" | tail -1)"
        else
            echo "FAILED"; echo "$out" | tail -15; failed=1
        fi
    done
    exit $failed

# Lint, type check and tests
check: lint typecheck test

# Build the images in docs/images/ from the scripts in examples/
images:
    uv run python scripts/build_images.py

# Serve docs locally
docs: images
    uv run zensical serve

# Build docs, failing on warnings and on unresolved cross-references
docs-build: images
    uv run zensical build --strict --clean
    uv run python scripts/check_site.py

# Build sdist and wheel
build:
    uv build

# Remove build and cache artefacts
clean:
    rm -rf build dist site .pytest_cache .ruff_cache .coverage
    find . -name __pycache__ -type d -prune -not -path "./.venv/*" -exec rm -rf {} +
