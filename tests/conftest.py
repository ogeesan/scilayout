"""Shared test configuration."""

from collections.abc import Generator

import matplotlib

matplotlib.use("Agg")  # headless backend so tests behave the same everywhere

import matplotlib.pyplot as plt
import pytest

import scilayout
from scilayout import style


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
