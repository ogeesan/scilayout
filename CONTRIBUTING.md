# Contributing

Thank you for your interest in contributing to scilayout.

## Getting started

1. Fork the repository and clone your fork.
2. Install [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/).
3. Run `uv sync` to install the project and its development tools.
4. Optionally run `uvx pre-commit install` to lint and format on every commit.
5. Make your change on a branch, then open a pull request.

## Checks

`just` lists every recipe.
The ones you will use most:

| Command | What it does |
| --- | --- |
| `just check` | Lint, type check and run the tests. |
| `just format` | Format the code with ruff. |
| `just cov` | Run the tests and show uncovered lines. |
| `just visual` | Run the visual tests and keep their SVG and PNG output in `test_outputs/` to look at. |
| `just compat` | Run the tests against several matplotlib versions (needs network). |
| `just images` | Build the README and documentation images from the scripts in `examples/`. |
| `just docs` | Serve the documentation locally. |
| `just docs-build` | Build the documentation and fail on warnings or broken cross-references. |

Continuous integration runs the same checks on Linux, macOS and Windows.

## Guidelines

- Add tests for new behaviour.
- Write docstrings in numpydoc style.
  The API reference is built from them.
- Add a line to the "Unreleased" section of `CHANGELOG.md` for any change a user would notice.
- Scilayout supports matplotlib 3.5 or newer, numpy 1.21.3 or newer and Python 3.10 or newer.
- In Markdown files, write one sentence per line.

## Reporting issues

Open an issue on GitHub and fill in the template.
The matplotlib version, the backend and your operating system matter for most layout bugs.
