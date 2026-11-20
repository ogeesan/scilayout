"""Build a representative figure, export it to SVG and check where everything is.

Positions are read back out of the SVG (the thing a journal or Illustrator would see),
and compared with where the figure was *asked* to put them, in cm from the upper left.

To look at the result, run ``pytest --keep-outputs tests/test_layout_svg.py`` (or
``just visual``) and open, in ``test_outputs/``:

- ``layout.svg`` / ``layout.png``: the figure
- ``layout_with_grid.svg`` / ``layout_with_grid.png``: the same figure with the cm
  guide grid on top (major markers every 5 cm, minor every 1 cm, half-cm crosses)
"""

import re
from collections.abc import Generator
from dataclasses import dataclass
from xml.etree.ElementTree import Element

import matplotlib.pyplot as plt
import pytest
from defusedxml.ElementTree import parse
from matplotlib.text import Text

import scilayout
from scilayout.classes import FigureText, PanelAxes, SciFigure
from scilayout.scalebars import LinkedScaleBar, ScaleBar
from scilayout.stats import StatsLine

SVG = {"svg": "http://www.w3.org/2000/svg"}
CM_PER_PT = 2.54 / 72  # SVG units are points
TOL = 0.005  # cm, about 0.05 mm

FIG_W, FIG_H = 12.0, 8.0

# The panels asked for, as (x, y, width, height) in cm from the upper left.
# All have data limits 0-10 on both axes, which makes expected positions easy to derive.
PANELS = {
    "a": (1.5, 1.5, 4.5, 2.5),
    "b": (7.0, 1.5, 4.5, 2.5),
    "c": (1.5, 5.5, 9.5, 1.7),
}


@dataclass
class Rect:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0


def data_to_cm(panel: str, x: float, y: float) -> tuple[float, float]:
    """Where data coordinates (0-10 on each axis) land on the page, in cm."""
    px, py, w, h = PANELS[panel]
    return px + x / 10 * w, py + h - y / 10 * h


def axes_fraction_to_cm(panel: str, fx: float, fy: float) -> tuple[float, float]:
    px, py, w, h = PANELS[panel]
    return px + fx * w, py + (1 - fy) * h


# --- reading the SVG ---


def numbers(path_data: str) -> list[float]:
    return [float(n) for n in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", path_data)]


def group(root: Element, gid: str) -> Element:
    found = root.find(f'.//svg:g[@id="{gid}"]', SVG)
    assert found is not None, f"no element with gid {gid!r} in the SVG"
    return found


def path_segments(root: Element, gid: str) -> list[list[tuple[float, float]]]:
    """The sub-paths of a line, as lists of (x, y) points in cm."""
    path = group(root, gid).find(".//svg:path", SVG)
    assert path is not None
    segments = []
    for piece in path.attrib["d"].split("M")[1:]:
        values = numbers(piece)
        segments.append(
            [
                (values[i] * CM_PER_PT, values[i + 1] * CM_PER_PT)
                for i in range(0, len(values), 2)
            ]
        )
    return segments


def rect_of(root: Element, gid: str) -> Rect:
    """Bounding box of the first path in a group, in cm."""
    points = [p for segment in path_segments(root, gid) for p in segment]
    xs, ys = zip(*points, strict=True)
    return Rect(min(xs), min(ys), max(xs), max(ys))


@dataclass
class TextInfo:
    x: float
    y: float
    anchor: str
    content: str
    rotation: float
    fontsize: float


def text_of(root: Element, gid: str) -> TextInfo:
    """Anchor point (cm), alignment and content of a text element.

    ``x, y`` is the anchor SVG uses: the baseline at the alignment point. Horizontal
    text has ``x``, ``y`` and a ``text-anchor`` (start, middle or end). Rotated text
    is written as ``translate(x y) rotate(angle)`` and always starts at that point.
    """
    text = group(root, gid).find(".//svg:text", SVG)
    assert text is not None
    style = text.attrib["style"]
    transform = text.attrib.get("transform", "")
    rotate = re.search(r"rotate\((-?[\d.]+)", transform)
    translate = re.search(r"translate\(([-\d.]+) ([-\d.]+)\)", transform)
    if "x" in text.attrib:
        x, y = float(text.attrib["x"]), float(text.attrib["y"])
    else:
        assert translate is not None
        x, y = float(translate.group(1)), float(translate.group(2))
    anchor = re.search(r"text-anchor: (\w+)", style)
    return TextInfo(
        x=x * CM_PER_PT,
        y=y * CM_PER_PT,
        anchor=anchor.group(1) if anchor else "start",
        content=(text.text or "").strip(),
        rotation=float(rotate.group(1)) if rotate else 0.0,
        fontsize=float(re.search(r"font-size: ([\d.]+)px", style).group(1)),  # pyright: ignore[reportOptionalMemberAccess]
    )


def tag(artist, gid: str) -> None:
    artist.set_gid(gid)


# --- building the figure ---


def build_figure() -> SciFigure:
    fig = scilayout.figure()
    fig.set_size_cm(FIG_W, FIG_H)

    axes: dict[str, PanelAxes] = {}
    for name, location in PANELS.items():
        ax = fig.add_panel(location, panellabel=name, method="bounds")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_gid(f"panel-{name}")
        assert ax.panellabel is not None
        tag(ax.panellabel.text, f"label-{name}")
        axes[name] = ax

    # a: a plain scale bar, text below
    bar = ScaleBar(axes["a"], (1, 4), 2, unit="s", coordSystem="data")
    tag(bar.line, "a-bar")
    tag(bar.text, "a-bar-text")

    # b: scale bars with their text centred in a break in the bar, and a stats line
    xbar = ScaleBar(axes["b"], (2, 5), 6, unit="s", coordSystem="data", vpos="center")
    tag(xbar.line, "b-xbar")
    tag(xbar.text, "b-xbar-text")
    ybar = ScaleBar(
        axes["b"],
        (9, 1),
        7,
        unit="mV",
        coordSystem="data",
        orientation="v",
        hpos="center",
    )
    tag(ybar.line, "b-ybar")
    tag(ybar.text, "b-ybar-text")
    stats = StatsLine(axes["b"], 0.9, 2, 8)
    assert stats.main_bar and stats.left_drop and stats.right_drop
    tag(stats.main_bar[0], "b-stats-bar")
    tag(stats.left_drop[0], "b-stats-left")
    tag(stats.right_drop[0], "b-stats-right")

    # c: linked scale bars sharing a corner
    linked = LinkedScaleBar(
        axes["c"], (6, 4), 3, 4, x_unit="s", y_unit="mV", coordSystem="data"
    )
    tag(linked.x_scalebar.line, "c-xbar")
    tag(linked.x_scalebar.text, "c-xbar-text")
    tag(linked.y_scalebar.line, "c-ybar")
    tag(linked.y_scalebar.text, "c-ybar-text")

    # figure level text, in cm from the upper left
    title = FigureText(0.3, 0.6, "Layout check", fig)
    tag(title.text, "title")

    return fig


@pytest.fixture(scope="module")
def layout(output_dir) -> Generator[SciFigure, None, None]:
    """The figure, with its SVG and PNG written to ``output_dir``."""
    fig = build_figure()
    fig.export(output_dir / "layout.svg", bbox=None)  # no tight crop: fixed page origin
    fig.export(output_dir / "layout.png", bbox=None, transparent_png=False)
    yield fig
    plt.close(fig)


@pytest.fixture(scope="module")
def root(layout, output_dir) -> Generator[Element, None, None]:
    """The parsed SVG. Also writes a copy with the cm grid on, for looking at."""
    tree_root = parse(output_dir / "layout.svg").getroot()
    assert tree_root is not None

    gridded = build_figure()
    gridded.draw_grid()
    gridded.export(output_dir / "layout_with_grid.svg", bbox=None)
    gridded.export(
        output_dir / "layout_with_grid.png", bbox=None, transparent_png=False
    )
    plt.close(gridded)
    yield tree_root


# --- the checks ---


class TestPage:
    def test_page_size_in_cm(self, root):
        width = float(root.attrib["width"].removesuffix("pt")) * CM_PER_PT
        height = float(root.attrib["height"].removesuffix("pt")) * CM_PER_PT
        assert width == pytest.approx(FIG_W, abs=TOL)
        assert height == pytest.approx(FIG_H, abs=TOL)

    @pytest.mark.parametrize("name", ["layout", "layout_with_grid"])
    @pytest.mark.parametrize("suffix", [".svg", ".png"])
    def test_outputs_were_written_for_viewing(self, root, output_dir, name, suffix):
        assert (output_dir / f"{name}{suffix}").stat().st_size > 0

    def test_grid_version_has_more_markers_than_plain(self, root, output_dir):
        plain = (output_dir / "layout.svg").stat().st_size
        gridded = (output_dir / "layout_with_grid.svg").stat().st_size
        assert gridded > plain


class TestPanels:
    @pytest.mark.parametrize("name", PANELS)
    def test_panel_is_where_it_was_asked_to_be(self, root, name):
        x, y, w, h = PANELS[name]
        rect = rect_of(root, f"panel-{name}")
        assert (rect.x0, rect.y0) == pytest.approx((x, y), abs=TOL)
        assert (rect.width, rect.height) == pytest.approx((w, h), abs=TOL)

    def test_panels_do_not_overlap_and_have_room_for_ticks(self, root):
        rects = {name: rect_of(root, f"panel-{name}") for name in PANELS}
        a, b, c = rects["a"], rects["b"], rects["c"]
        assert b.x0 - a.x1 >= 0.5  # side by side
        assert c.y0 - max(a.y1, b.y1) >= 1.2  # tick labels and the next row's label

    def test_everything_is_inside_the_page(self, root):
        for name in PANELS:
            rect = rect_of(root, f"panel-{name}")
            assert rect.x0 >= 0
            assert rect.y0 >= 0
            assert rect.x1 <= FIG_W
            assert rect.y1 <= FIG_H


class TestPanelLabels:
    @pytest.mark.parametrize("name", PANELS)
    def test_label_is_offset_from_the_panel_corner(self, root, name):
        x, y, _, _ = PANELS[name]
        style = scilayout.style.params
        label = text_of(root, f"label-{name}")
        assert label.content == name
        assert label.x == pytest.approx(x + style["panellabel.xoffset"], abs=TOL)
        assert label.y == pytest.approx(y + style["panellabel.yoffset"], abs=TOL)

    @pytest.mark.parametrize("name", PANELS)
    def test_label_sits_outside_the_panel_upper_left(self, root, name):
        panel = rect_of(root, f"panel-{name}")
        label = text_of(root, f"label-{name}")
        assert label.x < panel.x0
        assert label.y < panel.y0  # baseline is above the top edge
        assert panel.y0 - label.y < 0.5  # ...but close to it
        assert label.x >= 0  # and still on the page

    def test_labels_use_the_default_style(self, root):
        label = text_of(root, "label-a")
        assert label.fontsize == scilayout.style.params["panellabel.fontsize"]
        assert label.anchor == "start"  # text starts at the offset position


class TestHorizontalScaleBar:
    def test_bar_position_and_length(self, root):
        (segment,) = path_segments(root, "a-bar")
        (x0, y0), (x1, y1) = segment
        expected_start = data_to_cm("a", 1, 4)
        expected_end = data_to_cm("a", 3, 4)
        assert (x0, y0) == pytest.approx(expected_start, abs=TOL)
        assert (x1, y1) == pytest.approx(expected_end, abs=TOL)
        assert x1 - x0 == pytest.approx(2 / 10 * PANELS["a"][2], abs=TOL)

    def test_text_is_centred_under_the_bar_with_padding(self, root):
        (x0, y), (x1, _) = path_segments(root, "a-bar")[0]
        text = text_of(root, "a-bar-text")
        assert text.content == "2 s"
        assert text.anchor == "middle"
        assert text.x == pytest.approx((x0 + x1) / 2, abs=TOL)
        # baseline is below the bar, by a text height or so: padding plus the
        # text's own ascent, a few mm for 8 pt text
        assert 0.15 < text.y - y < 0.5

    def test_bar_is_inside_its_panel(self, root):
        panel = rect_of(root, "panel-a")
        (x0, y), (x1, _) = path_segments(root, "a-bar")[0]
        assert panel.x0 < x0 < x1 < panel.x1
        assert panel.y0 < y < panel.y1


class TestCentredScaleBars:
    def test_horizontal_bar_is_split_around_the_text(self, root):
        left, right = path_segments(root, "b-xbar")
        start = data_to_cm("b", 2, 5)
        end = data_to_cm("b", 8, 5)
        assert left[0] == pytest.approx(start, abs=TOL)
        assert right[-1] == pytest.approx(end, abs=TOL)
        # both halves are on the same horizontal line
        assert {round(y, 3) for _, y in left + right} == {round(start[1], 3)}
        gap = right[0][0] - left[-1][0]
        assert 0.3 < gap < (end[0] - start[0])

    def test_horizontal_text_sits_in_the_middle_of_the_gap(self, root):
        left, right = path_segments(root, "b-xbar")
        text = text_of(root, "b-xbar-text")
        gap_middle = (left[-1][0] + right[0][0]) / 2
        assert text.content == "6 s"
        assert text.x == pytest.approx(gap_middle, abs=TOL)
        # baseline a little below the bar's line: text is vertically centred on it
        bar_y = left[0][1]
        assert 0 < text.y - bar_y < 0.15

    def test_text_fits_in_the_gap_with_padding(self, root):
        left, right = path_segments(root, "b-xbar")
        text = text_of(root, "b-xbar-text")
        gap = right[0][0] - left[-1][0]
        # an 8 pt "6 s" is about 0.4 cm wide; the gap must be wider than the text
        # but not by much (padding on each side is half a text height)
        text_width_estimate = len(text.content) * text.fontsize * 0.6 * CM_PER_PT
        assert text_width_estimate * 0.7 < gap < text_width_estimate + 1.0

    def test_vertical_bar_is_split_around_the_text(self, root):
        lower, upper = path_segments(root, "b-ybar")
        start = data_to_cm("b", 9, 1)
        end = data_to_cm("b", 9, 8)
        assert lower[0] == pytest.approx(start, abs=TOL)
        assert upper[-1] == pytest.approx(end, abs=TOL)
        # SVG y grows downwards, so the lower half starts below the gap
        assert lower[0][1] > lower[-1][1] > upper[0][1] > upper[-1][1]

    def test_vertical_text_is_rotated_and_in_the_gap(self, root):
        lower, upper = path_segments(root, "b-ybar")
        text = text_of(root, "b-ybar-text")
        assert text.content == "7 mV"
        assert text.rotation == pytest.approx(-90)
        # rotated text starts at its anchor and runs up the page (towards smaller y),
        # so its centre is half its length above the anchor
        gap_start, gap_end = upper[0][1], lower[-1][1]
        gap_middle = (gap_start + gap_end) / 2
        text_length = 2 * (text.y - gap_middle)
        assert gap_start < text.y <= gap_end
        assert 0.3 < text_length < gap_end - gap_start  # fits, with padding
        bar_x = lower[0][0]
        assert abs(text.x - bar_x) < 0.2  # on the bar, not off to the side


class TestStatsLine:
    def test_bar_spans_the_requested_data_range_at_the_axes_fraction(self, root):
        ((x0, y0), (x1, y1)) = path_segments(root, "b-stats-bar")[0]
        expected_start = axes_fraction_to_cm("b", 0.2, 0.9)
        expected_end = axes_fraction_to_cm("b", 0.8, 0.9)
        assert (x0, y0) == pytest.approx(expected_start, abs=TOL)
        assert (x1, y1) == pytest.approx(expected_end, abs=TOL)

    @pytest.mark.parametrize(("side", "fx"), [("left", 0.2), ("right", 0.8)])
    def test_drops_hang_down_from_each_end_of_the_bar(self, root, side, fx):
        ((x0, y0), (x1, y1)) = path_segments(root, f"b-stats-{side}")[0]
        top = axes_fraction_to_cm("b", fx, 0.9)
        assert (x0, y0) == pytest.approx(top, abs=TOL)
        assert x1 == pytest.approx(x0, abs=TOL)
        drop = y1 - y0
        assert drop == pytest.approx(0.025 * PANELS["b"][3], abs=TOL)
        assert drop > 0  # downwards

    def test_stats_line_is_inside_the_panel(self, root):
        panel = rect_of(root, "panel-b")
        bar = rect_of(root, "b-stats-bar")
        assert panel.x0 < bar.x0 < bar.x1 < panel.x1
        assert panel.y0 < bar.y0 < panel.y1


class TestLinkedScaleBars:
    def test_share_a_corner(self, root):
        corner = data_to_cm("c", 6, 4)
        (xbar,) = path_segments(root, "c-xbar")
        (ybar,) = path_segments(root, "c-ybar")
        assert xbar[0] == pytest.approx(corner, abs=TOL)
        assert ybar[0] == pytest.approx(corner, abs=TOL)

    def test_lengths_follow_each_axis(self, root):
        (xbar,) = path_segments(root, "c-xbar")
        (ybar,) = path_segments(root, "c-ybar")
        _, _, w, h = PANELS["c"]
        assert xbar[1][0] - xbar[0][0] == pytest.approx(3 / 10 * w, abs=TOL)
        assert ybar[0][1] - ybar[1][1] == pytest.approx(4 / 10 * h, abs=TOL)

    def test_labels_are_on_the_outside_of_each_bar(self, root):
        (xbar,) = path_segments(root, "c-xbar")
        (ybar,) = path_segments(root, "c-ybar")
        xtext = text_of(root, "c-xbar-text")
        ytext = text_of(root, "c-ybar-text")
        assert xtext.y > xbar[0][1]  # below the horizontal bar
        assert ytext.x < ybar[0][0]  # left of the vertical bar
        assert ytext.rotation == pytest.approx(-90)


class TestFigureText:
    def test_title_is_at_the_requested_cm_position(self, root):
        title = text_of(root, "title")
        assert title.content == "Layout check"
        assert title.x == pytest.approx(0.3, abs=TOL)
        assert title.y == pytest.approx(0.6, abs=TOL)

    def test_title_is_above_the_panels(self, root):
        title = text_of(root, "title")
        top_of_panels = min(rect_of(root, f"panel-{name}").y0 for name in PANELS)
        assert title.y < top_of_panels - 0.3  # clear of panel labels as well


class TestNothingCollides:
    """Rendered text should not run into other text (checked on the live figure)."""

    @staticmethod
    def visible_texts(fig: SciFigure) -> list[Text]:
        fig.canvas.draw()
        texts = list(fig.texts)
        for ax in fig.axes:
            texts += ax.texts + ax.get_xticklabels() + ax.get_yticklabels()
        return [t for t in texts if t.get_visible() and t.get_text().strip()]

    def test_no_text_overlaps_other_text(self, layout):
        renderer = layout.canvas.get_renderer()  # pyright: ignore[reportAttributeAccessIssue]
        texts = self.visible_texts(layout)
        boxes = [(t, t.get_window_extent(renderer)) for t in texts]
        # tick labels that matplotlib keeps but doesn't show sit outside the figure
        boxes = [(t, b) for t, b in boxes if layout.bbox.containsx(b.x0)]
        collisions = [
            (a.get_text(), b.get_text())
            for i, (a, box_a) in enumerate(boxes)
            for b, box_b in boxes[i + 1 :]
            if box_a.overlaps(box_b)
        ]
        assert collisions == []

    @pytest.mark.parametrize("name", PANELS)
    def test_panel_label_clears_its_tick_labels(self, layout, name):
        renderer = layout.canvas.get_renderer()  # pyright: ignore[reportAttributeAccessIssue]
        layout.canvas.draw()
        ax = next(a for a in layout.axes if a.get_gid() == f"panel-{name}")
        assert isinstance(ax, PanelAxes)
        assert ax.panellabel is not None
        label_box = ax.panellabel.text.get_window_extent(renderer)
        for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
            if tick_label.get_text():
                assert not label_box.overlaps(tick_label.get_window_extent(renderer))
