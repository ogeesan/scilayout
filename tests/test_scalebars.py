import numpy as np
import pytest

from scilayout import style
from scilayout.scalebars import LinkedScaleBar, ScaleBar


def line_xy(bar: ScaleBar) -> tuple[list[float], list[float]]:
    x = np.asarray(bar.line.get_xdata(), dtype=float).tolist()
    y = np.asarray(bar.line.get_ydata(), dtype=float).tolist()
    return x, y


class TestScaleBarPlacement:
    def test_horizontal_data_coordinates(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, unit="mm", coordSystem="data")
        x, y = line_xy(bar)
        assert x == pytest.approx([3, 5])
        assert y == pytest.approx([4, 4])

    def test_vertical_data_coordinates(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, unit="mm", coordSystem="data", orientation="v")
        x, y = line_xy(bar)
        assert x == pytest.approx([3, 3])
        assert y == pytest.approx([4, 6])

    @pytest.mark.parametrize("orientation", ["h", "horizontal"])
    def test_horizontal_aliases(self, panel, orientation):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data", orientation=orientation)
        assert bar.orientation == "h"

    def test_fraction_coordinates(self, panel):
        bar = ScaleBar(panel, (0.5, 0.25), 2, coordSystem="fraction")
        x, y = line_xy(bar)
        assert x == pytest.approx([5, 7])
        assert y == pytest.approx([2, 2])

    def test_cm_coordinates(self, panel):
        # panel spans 2-7 cm (x) over data 0-10, and 2-6 cm (y) over data 8-0
        bar = ScaleBar(panel, (4.5, 4), 2, coordSystem="cm")
        x, y = line_xy(bar)
        assert x == pytest.approx([5, 7])
        assert y == pytest.approx([4, 4])

    def test_cm_requires_panel_axes(self, scifig):
        ax = scifig.add_axes((0.1, 0.1, 0.5, 0.5))
        with pytest.raises(TypeError, match="PanelAxes"):
            ScaleBar(ax, (1, 1), 1, coordSystem="cm")

    def test_move_with_default_coordinate_system(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        bar.move(1, 2)
        x, y = line_xy(bar)
        assert x == pytest.approx([1, 3])
        assert y == pytest.approx([2, 2])

    def test_move_with_different_coordinate_system(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        bar.move(0.5, 0.25, coordSystem="fraction")
        x, y = line_xy(bar)
        assert x == pytest.approx([5, 7])
        assert y == pytest.approx([2, 2])

    def test_axis_limits_are_preserved(self, panel):
        ScaleBar(panel, (3, 4), 2, coordSystem="data")
        assert panel.get_xlim() == (0, 10)
        assert panel.get_ylim() == (0, 8)

    def test_line_is_not_clipped(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        assert not bar.line.get_clip_on()


class TestScaleBarText:
    def test_default_text_uses_length_and_unit(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, unit="mm", coordSystem="data")
        assert bar.text.get_text() == "2 mm"

    def test_custom_text(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, textstring="two", coordSystem="data")
        assert bar.text.get_text() == "two"

    def test_horizontal_text_is_centred_below_by_default(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, unit="mm", coordSystem="data")
        x, y = bar.text.get_position()
        assert x == pytest.approx(4)  # middle of 3 to 5
        assert y < 4
        assert bar.text.get_verticalalignment() == "top"
        assert bar.text.get_rotation() == 0

    def test_horizontal_text_above_when_vpos_top(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, unit="mm", coordSystem="data", vpos="top")
        assert bar.text.get_position()[1] > 4
        assert bar.text.get_verticalalignment() == "bottom"

    def test_vertical_text_is_rotated_and_to_the_left_by_default(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, unit="mm", coordSystem="data", orientation="v")
        x, y = bar.text.get_position()
        assert x < 3
        assert y == pytest.approx(5)  # middle of 4 to 6
        assert bar.text.get_rotation() == 90
        assert bar.text.get_horizontalalignment() == "right"

    def test_vertical_text_on_the_right(self, panel):
        bar = ScaleBar(
            panel, (3, 4), 2, coordSystem="data", orientation="v", hpos="right"
        )
        assert bar.text.get_position()[0] > 3
        assert bar.text.get_horizontalalignment() == "left"


class TestScaleBarStyle:
    def test_fontsize_and_linewidth_defaults(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        assert bar.text.get_fontsize() == 8
        assert bar.line.get_linewidth() == 1

    def test_fontsize_and_linewidth_overrides(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data", lw=3, fontsize=14)
        assert bar.text.get_fontsize() == 14
        assert bar.line.get_linewidth() == 3

    def test_fontsize_default_follows_style(self, panel):
        style.params["scalebars.fontsize"] = 11
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        assert bar.text.get_fontsize() == 11


class TestScaleBarValidation:
    def test_transaxes_not_implemented(self, panel):
        with pytest.raises(NotImplementedError):
            ScaleBar(panel, (3, 4), 2, transform="transAxes")

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"coordSystem": "furlongs"},
            {"transform": "transFigure"},
            {"vpos": "left"},
            {"orientation": "v", "hpos": "top"},
            {"orientation": "diagonal"},
        ],
    )
    def test_invalid_options_raise(self, panel, kwargs):
        with pytest.raises(ValueError, match="must be"):
            ScaleBar(panel, (3, 4), 2, **kwargs)

    def test_move_with_invalid_coordinate_system_raises(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        with pytest.raises(ValueError, match="coordSystem"):
            bar.move(1, 1, coordSystem="furlongs")


class TestLinkedScaleBar:
    def test_creates_horizontal_and_vertical_bars(self, panel):
        linked = LinkedScaleBar(
            panel, (3, 4), 2, 1, x_unit="s", y_unit="mV", coordSystem="data"
        )
        assert linked.x_scalebar.orientation == "h"
        assert linked.y_scalebar.orientation == "v"
        assert linked.x_scalebar.text.get_text() == "2 s"
        assert linked.y_scalebar.text.get_text() == "1 mV"

    def test_bars_share_a_corner(self, panel):
        linked = LinkedScaleBar(panel, (3, 4), 2, 1, coordSystem="data")
        x_x, x_y = line_xy(linked.x_scalebar)
        y_x, y_y = line_xy(linked.y_scalebar)
        assert x_x == pytest.approx([3, 5])
        assert x_y == pytest.approx([4, 4])
        assert y_x == pytest.approx([3, 3])
        assert y_y == pytest.approx([4, 5])

    def test_move_moves_both(self, panel):
        linked = LinkedScaleBar(panel, (3, 4), 2, 1, coordSystem="data")
        linked.move(6, 1)
        x_x, x_y = line_xy(linked.x_scalebar)
        y_x, y_y = line_xy(linked.y_scalebar)
        assert x_x == pytest.approx([6, 8])
        assert x_y == pytest.approx([1, 1])
        assert y_x == pytest.approx([6, 6])
        assert y_y == pytest.approx([1, 2])

    def test_move_with_coordinate_system(self, panel):
        linked = LinkedScaleBar(panel, (3, 4), 2, 1, coordSystem="data")
        linked.move(0.5, 0.25, coordSystem="fraction")
        assert np.allclose(line_xy(linked.x_scalebar)[0], [5, 7])
