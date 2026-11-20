"""A picture of scale bar padding, with guides showing where the text should be.

Run ``pytest --keep-outputs tests/test_padding_visual.py`` (or ``just visual``) and open
``test_outputs/padding.svg`` or ``padding.png``.

Each cell is a scale bar with a different ``pad`` (columns) and text position (rows),
drawn with a thin line (left panel) and a thick one (right panel). Red hairlines mark
where the text is *meant* to be:

- beside the bar: ``pad`` cm from the edge of the line, so the text should touch the red
  line and never cross it
- centred on the bar: ``pad`` cm either side of the text, so the visible ends of the bar
  should meet the red lines

The test also measures every cell and fails if the text is not on its guide, so the
picture can't quietly disagree with the numbers.
"""

from collections.abc import Generator
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.lines import Line2D

import scilayout
from scilayout.classes import PanelAxes, SciFigure
from scilayout.scalebars import ScaleBar

CM_PER_POINT = 2.54 / 72
PADS = [0, 0.1, 0.2, 0.4]  # cm, one column each
LINEWIDTHS = [1, 6]  # points, one panel each
HEADER = 1.4  # cm above the first row
LABEL_WIDTH = 4.0  # cm left of the first column for row labels
COLUMN = 2.6  # cm per column
ROW = 2.4  # cm per row
BAR = 2.0  # cm, length of every bar
TOLERANCE = 0.005  # cm

# (row label, ScaleBar options, "h" or "v", how the text sits)
VARIANTS = [
    ("text below", {}, "h", "below"),
    ("text above", {"vpos": "top"}, "h", "above"),
    ("vertical, text left", {"orientation": "v"}, "v", "left"),
    ("vertical, text right", {"orientation": "v", "hpos": "right"}, "v", "right"),
    ("text centred", {"vpos": "center"}, "h", "centre"),
    (
        "vertical, text centred",
        {"orientation": "v", "hpos": "center"},
        "v",
        "centre",
    ),
]

PANEL_WIDTH = LABEL_WIDTH + COLUMN * len(PADS)
PANEL_HEIGHT = HEADER + ROW * len(VARIANTS)
MARGIN = 1.0
FIG_WIDTH = MARGIN * 3 + PANEL_WIDTH * len(LINEWIDTHS)
FIG_HEIGHT = MARGIN * 2 + PANEL_HEIGHT


@dataclass
class Cell:
    """One scale bar, and how far its text is from where it should be."""

    description: str
    error_cm: float


def guide(ax: PanelAxes, xs: list[float], ys: list[float]) -> Line2D:
    """A red hairline marking where an edge should be (data units are cm here)."""
    return ax.plot(xs, ys, color="red", lw=0.3, zorder=10, clip_on=False)[0]


def text_box(bar: ScaleBar) -> tuple[float, float, float, float]:
    """The text's (left, right, top, bottom) in cm on the page: y grows downwards."""
    fig = bar.ax.get_figure()
    renderer = fig.canvas.get_renderer()  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    box = bar.text.get_window_extent(renderer).transformed(bar.ax.transData.inverted())
    return box.x0, box.x1, min(box.y0, box.y1), max(box.y0, box.y1)


def visible_ends(bar: ScaleBar) -> tuple[float, float]:
    """Where the two halves of a split bar visibly end, after the line caps.

    The caps stick out half a line width past the end of each piece, into the break.
    """
    xs = np.asarray(bar.line.get_xdata(), dtype=float)
    ys = np.asarray(bar.line.get_ydata(), dtype=float)
    values = xs if bar.orientation == "h" else ys
    nan = int(np.flatnonzero(np.isnan(values))[0])
    half_cap = bar.line.get_linewidth() * CM_PER_POINT / 2
    low, high = values[nan - 1], values[nan + 1]
    return low + half_cap, high - half_cap


def add_cell(
    ax: PanelAxes, row: int, column: int, pad: float, lw: float
) -> tuple[ScaleBar, Cell]:
    label, options, orientation, text_side = VARIANTS[row]
    # data units are cm, with y growing downwards, so positions are cm on the panel
    x = LABEL_WIDTH + column * COLUMN + (0.4 if orientation == "h" else 1.0)
    y = HEADER + row * ROW + (1.0 if orientation == "h" else 0.2)
    bar = ScaleBar(
        ax, (x, y), BAR, textstring="2 s" if orientation == "h" else "2 mV",
        coordSystem="data", lw=lw, pad=pad, **options,
    )  # fmt: skip
    from_centre = pad + lw * CM_PER_POINT / 2
    left, right, top, bottom = text_box(bar)
    description = f"{label}, pad {pad}, lw {lw}"

    if text_side == "below":
        guide(ax, [x, x + BAR], [y + from_centre] * 2)
        error = top - (y + from_centre)
    elif text_side == "above":
        guide(ax, [x, x + BAR], [y - from_centre] * 2)
        error = (y - from_centre) - bottom
    elif text_side == "left":
        guide(ax, [x - from_centre] * 2, [y, y + BAR])
        error = (x - from_centre) - right
    elif text_side == "right":
        guide(ax, [x + from_centre] * 2, [y, y + BAR])
        error = left - (x + from_centre)
    else:  # centred: the visible gap is the text plus pad either side
        first, second = visible_ends(bar)
        if orientation == "h":
            want = (left - pad, right + pad)
            guide(ax, [want[0]] * 2, [y - 0.5, y + 0.5])
            guide(ax, [want[1]] * 2, [y - 0.5, y + 0.5])
        else:
            want = (top - pad, bottom + pad)
            guide(ax, [x - 0.5, x + 0.5], [want[0]] * 2)
            guide(ax, [x - 0.5, x + 0.5], [want[1]] * 2)
        error = max(abs(first - want[0]), abs(second - want[1]))
    return bar, Cell(description, abs(error))


def build_figure() -> tuple[SciFigure, list[Cell]]:
    fig = scilayout.figure()
    fig.set_size_cm(FIG_WIDTH, FIG_HEIGHT)
    cells: list[Cell] = []
    for panel_index, lw in enumerate(LINEWIDTHS):
        left = MARGIN + panel_index * (PANEL_WIDTH + MARGIN)
        ax = fig.add_panel((left, MARGIN, PANEL_WIDTH, PANEL_HEIGHT), method="bounds")
        ax.set_xlim(0, PANEL_WIDTH)  # one data unit is one cm...
        ax.set_ylim(PANEL_HEIGHT, 0)  # ...with y downwards, like the page
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"line width {lw} pt", fontsize=9, loc="left")
        for column, pad in enumerate(PADS):
            ax.text(
                LABEL_WIDTH + column * COLUMN + COLUMN / 2,
                HEADER / 2,
                f"pad {pad} cm",
                ha="center",
                va="center",
                fontsize=8,
                color="gray",
            )
        for row, (label, *_) in enumerate(VARIANTS):
            ax.text(
                0.2,
                HEADER + row * ROW + ROW / 2,
                label,
                ha="left",
                va="center",
                fontsize=8,
                color="gray",
            )
            for column, pad in enumerate(PADS):
                cells.append(add_cell(ax, row, column, pad, lw)[1])
    return fig, cells


@pytest.fixture(scope="module")
def picture(output_dir) -> Generator[list[Cell], None, None]:
    fig, cells = build_figure()
    fig.export(output_dir / "padding.svg", bbox=None)
    fig.export(output_dir / "padding.png", bbox=None, dpi=200, transparent_png=False)
    plt.close(fig)
    yield cells


def test_picture_is_written_for_viewing(picture, output_dir):
    assert (output_dir / "padding.svg").stat().st_size > 0
    assert (output_dir / "padding.png").stat().st_size > 0


def test_every_cell_was_drawn(picture):
    assert len(picture) == len(VARIANTS) * len(PADS) * len(LINEWIDTHS)


@pytest.mark.parametrize("index", range(len(VARIANTS) * len(PADS) * len(LINEWIDTHS)))
def test_text_is_where_its_guide_says(picture, index):
    cell = picture[index]
    assert cell.error_cm == pytest.approx(0, abs=TOLERANCE), cell.description
