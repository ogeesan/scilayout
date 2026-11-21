"""A multi-panel figure laid out in centimetres: the image at the top of the README."""

from pathlib import Path

import numpy as np
from matplotlib.axes import Axes

import scilayout
from scilayout import FigureText, LinkedScaleBar, ScaleBar, StatsLine

FORMATS = ("png",)
DATA = Path(__file__).parent / "data"
RNG = np.random.default_rng(1)


def make() -> scilayout.SciFigure:
    """Build the figure."""
    fig = scilayout.figure()
    fig.set_size_cm(16, 6.5)

    # panels: (x, y, width, height) in cm from the upper left
    panel_a = fig.add_panel((2.1, 1.6, 6.2, 3.6), panellabel="a", method="bounds")
    panel_b = fig.add_panel((10, 1.6, 2.5, 3.6), panellabel="b", method="bounds")
    panel_c = fig.add_panel((13.6, 1.6, 2.2, 3.6), panellabel="c", method="bounds")

    # the panels are matplotlib axes, so plot into them as usual
    plot_hockey_stick(panel_a)
    ScaleBar(panel_a, (-50, -0.6), 0.5, "°C", orientation="v", coordSystem="data")

    plot_groups(panel_b)
    StatsLine(panel_b, 0.93, 0, 1)
    panel_b.text(
        0.5,
        0.92,
        "**",
        transform=panel_b.transAxes,
        ha="center",
        va="bottom",
        fontsize=8,
    )

    plot_decay(panel_c)
    LinkedScaleBar(
        panel_c, (11, 4.5), 10, 3, x_unit="min", y_unit="a.u.", coordSystem="data"
    )

    # Actually, change your mind about the panel sizes and move them around a bit. The figure will update automatically.
    panel_a.set_location((2.1, 1.5, 6.2, 3.5), method="bounds")

    # Sugar for the reader
    add_cm_ruler(fig)
    FigureText(
        2.0,
        0.25,
        "Panels placed in cm from the upper left",
        fig,
        size=8,
        ha="left",
        va="center",
    )
    return fig


def add_cm_ruler(
    fig: scilayout.SciFigure,
    length: float = 1,
    solid: float = 2.5,
    fade_length: float = 4.5,
) -> None:
    """Show that the figure is measured in cm from the upper left.

    Adds a grid of dots every 0.5 cm that fades out with distance from the upper left
    corner, and a pair of scale bars in that corner.
    """
    # an invisible axes over the whole figure, with its data in cm from the upper left
    width, height = fig.get_size_inches() * 2.54
    ruler = fig.add_panel((0, 0, width, height), method="bounds")
    ruler.axis("off")
    ruler.set_xlim(0, width)
    ruler.set_ylim(height, 0)
    ruler.set_zorder(-1)  # behind the panels

    # a dot every 0.5 cm: solid within ``solid`` cm of the corner, then fading over ``fade_length`` cm
    x, y = np.meshgrid(np.arange(0, width, 0.5), np.arange(0, height, 0.5))
    fade = np.clip(1 - (np.hypot(x, y) - solid) / fade_length, 0, 1).ravel() ** 1.5
    colours = np.zeros((fade.size, 4))
    colours[:, 3] = fade
    ruler.scatter(x.ravel(), y.ravel(), c=colours, marker="o", s=2, linewidths=0)

    LinkedScaleBar(
        ruler,
        (0.5, 0.5),
        length,
        length,
        "cm",
        "cm",
        coordSystem="data",
        hat="left",
        vat="top",
    )


def plot_hockey_stick(ax: Axes) -> None:
    """Plot the "hockey stick" of global mean temperature over the Common Era.

    Data from PAGES2k Consortium (Neukom et al. 2019), see the header of the CSV.
    """
    data = np.genfromtxt(
        DATA / "pages2k_gmst.csv", delimiter=",", names=True, skip_header=6
    )
    ax.fill_between(
        data["year"], data["p2_5"], data["p97_5"], color="#d9d9d9", linewidth=0
    )
    ax.plot(data["year"], data["median"], color="#344cd5", linewidth=0.75)
    ax.set_xlim(0, 2000)
    ax.set_ylim(-1.1, 0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_yticks([])
    ax.tick_params(labelsize=8)
    ax.set_xlabel("Year", fontsize=8)


def plot_groups(ax: Axes) -> None:
    """Plot two groups as bars with their individual points (made-up data)."""
    groups = {"control": RNG.normal(4.0, 0.8, 8), "treated": RNG.normal(6.0, 0.8, 8)}
    for i, values in enumerate(groups.values()):
        ax.bar(i, values.mean(), color=["#9e9e9e", "#d95f02"][i], width=0.7)
        jitter = RNG.normal(0, 0.07, values.size)
        ax.scatter(i + jitter, values, s=6, color="k", zorder=3)
    ax.set_xticks(range(2), list(groups), rotation=0, ha="center")
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("response (a.u.)", fontsize=8)
    ax.tick_params(labelsize=8)


def plot_decay(ax: Axes) -> None:
    """Plot a noisy exponential decay without axes (made-up data)."""
    x = np.linspace(0, 30, 200)
    y = 8 * np.exp(-x / 8) + 0.2 * RNG.standard_normal(x.size)
    ax.plot(x, y, color="#66b492", linewidth=1)
    ax.set_xlim(0, 30)
    ax.set_ylim(-1, 9)
    ax.axis("off")
