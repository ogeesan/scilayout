"""The social preview card: 2:1, for GitHub and for links shared on social media."""

import importlib.util
from pathlib import Path
from types import ModuleType

import scilayout
from scilayout import FigureText

FORMATS = ("png",)


def _load_hero() -> ModuleType:
    """Import ``hero.py`` next to this file, so the card reuses its plots."""
    spec = importlib.util.spec_from_file_location(
        "hero", Path(__file__).with_name("hero.py")
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make() -> scilayout.SciFigure:
    """Build the card (12.8 x 6.4 cm: 2560 x 1280 px at 200 dpi)."""
    hero = _load_hero()
    fig = scilayout.figure()
    fig.set_size_cm(12.8, 6.4)

    panel_a = fig.add_panel((5.4, 1.6, 3.5, 3.6), method="bounds")
    panel_b = fig.add_panel((10.1, 1.6, 2.3, 3.6), method="bounds")
    hero.plot_hockey_stick(panel_a)
    hero.plot_groups(panel_b)
    # fewer, smaller tick labels: the panels are small on the card
    panel_a.set_xticks([0, 1000, 2000])
    panel_b.tick_params(axis="x", labelsize=7)

    # a short fade, so the dots stay clear of the title
    hero.add_cm_ruler(fig, solid=1.5, fade_length=2.5)

    FigureText(0.6, 3.1, "scilayout", fig, size=24, weight="bold", va="center")
    FigureText(
        0.6,
        4.3,
        "Lay out matplotlib figures\nin cm from the upper left",
        fig,
        size=10,
        va="center",
        linespacing=1.4,
    )
    FigureText(
        0.6, 5.6, "pip install scilayout", fig, size=9, family="monospace", va="center"
    )
    return fig
