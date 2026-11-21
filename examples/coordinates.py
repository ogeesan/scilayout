"""The cm coordinate system, with the guide grid: used on the coordinates page."""

from typing import Any

import matplotlib.patches as patches

import scilayout

FORMATS = ("svg",)

ORANGE = "#d95f02"


def make() -> scilayout.SciFigure:
    """Build the figure."""
    fig = scilayout.figure()
    fig.set_size_cm(12, 7)

    # a panel 4.5 cm wide and 2.5 cm high, with its upper left corner at (1.5, 1.5)
    ax = fig.add_panel((1.5, 1.5, 4.5, 2.5), panellabel="a", method="bounds")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.draw_grid(major_interval=5, minor_interval=1)

    def arrow(start: tuple[float, float], end: tuple[float, float]) -> None:
        fig.add_artist(
            patches.FancyArrowPatch(
                start,
                end,
                transform=fig.transCM,  # cm from the upper left
                arrowstyle="-|>",
                mutation_scale=8,
                color=ORANGE,
                linewidth=1.2,
            )
        )

    def label(xy: tuple[float, float], text: str, **kwargs: Any) -> None:
        fig.text(
            *xy,
            text,
            transform=fig.transCM,
            color=ORANGE,
            fontsize=8,
            **kwargs,
        )

    # the axes, starting at the origin in the upper left
    arrow((0.3, 0.3), (3.2, 0.3))
    label((3.3, 0.3), "x (cm)", va="center")
    arrow((0.3, 0.3), (0.3, 3.2))
    label((0.1, 3.3), "y (cm)", ha="left", va="top")
    label((0.45, 0.45), "(0, 0)", ha="left", va="top")
    # the size of the panel
    arrow((1.5, 4.6), (6.0, 4.6))
    label((3.75, 4.8), "width 4.5", ha="center", va="top")
    arrow((6.7, 1.5), (6.7, 4.0))
    label((6.9, 2.75), "height 2.5", ha="left", va="center")
    label((1.6, 1.4), "(1.5, 1.5)", ha="left", va="bottom")
    return fig
