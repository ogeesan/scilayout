"""Shared test configuration."""

from collections.abc import Generator
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend so tests behave the same everywhere

import matplotlib.pyplot as plt
import pytest

import scilayout
from scilayout import style

OUTPUTS = Path(__file__).parent.parent / "test_outputs"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--keep-outputs",
        action="store_true",
        default=False,
        help="Write the figures some tests create (SVG and PNG) to test_outputs/ "
        "so they can be looked at. Without it they go to a temporary folder.",
    )


@pytest.fixture(scope="session")
def output_dir(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    """Where tests put figures: ``test_outputs/`` with --keep-outputs, else temporary."""
    if request.config.getoption("--keep-outputs"):
        OUTPUTS.mkdir(exist_ok=True)
        return OUTPUTS
    return tmp_path_factory.mktemp("outputs")


def pytest_report_header(config: pytest.Config) -> str | None:
    if config.getoption("--keep-outputs"):
        return f"keeping test figures in {OUTPUTS}"
    return None


@pytest.fixture(autouse=True)
def _reset_style() -> Generator[None, None, None]:
    """Stop style changes leaking between tests."""
    yield
    style.reset()


@pytest.fixture
def scifig() -> Generator[scilayout.classes.SciFigure, None, None]:
    """A 13 x 10 cm SciFigure."""
    figure = scilayout.figure()
    figure.set_size_cm(13, 10)
    yield figure
    plt.close(figure)


@pytest.fixture
def panel(
    scifig: scilayout.classes.SciFigure,
) -> scilayout.classes.PanelAxes:
    """A panel with extent (2, 2, 7, 6) cm and fixed limits 0-10 (x) and 0-8 (y)."""
    ax = scifig.add_panel((2, 2, 7, 6), method="extent")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    return ax
