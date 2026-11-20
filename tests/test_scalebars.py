import warnings

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

    def test_default_text_without_a_unit_is_just_the_length(self, panel):
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        assert bar.text.get_text() == "2"

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

    def test_linewidth_default_follows_style(self, panel):
        style.params["scalebars.linewidth"] = 2.5
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        assert bar.line.get_linewidth() == 2.5

    def test_explicit_linewidth_beats_style(self, panel):
        style.params["scalebars.linewidth"] = 2.5
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data", lw=4)
        assert bar.line.get_linewidth() == 4

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

    def test_find_x_y_rejects_unknown_coordinate_system(self, panel):
        # move() validates first, so this guards direct use of the private method
        bar = ScaleBar(panel, (3, 4), 2, coordSystem="data")
        with pytest.raises(ValueError, match="Unknown coordinate system"):
            bar._find_x_y(1, 1, "furlongs")

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


def text_extent_data(bar: ScaleBar) -> tuple[float, float, float, float]:
    """The text's bounding box (x0, y0, x1, y1) in data coordinates."""
    renderer = bar.ax.figure.canvas.get_renderer()  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    box = bar.text.get_window_extent(renderer).transformed(bar.ax.transData.inverted())
    return box.x0, box.y0, box.x1, box.y1


def segments(bar: ScaleBar) -> list[tuple[float, float]]:
    """The visible (start, end) of each piece of the bar along its length."""
    x, y = line_xy(bar)
    values = x if bar.orientation == "h" else y
    nan = [i for i, v in enumerate(values) if np.isnan(v)]
    assert len(nan) == 1
    return [
        (values[0], values[nan[0] - 1]),
        (values[nan[0] + 1], values[-1]),
    ]


class TestCentredText:
    def test_horizontal_text_is_on_the_bar(self, panel):
        bar = ScaleBar(panel, (2, 4), 6, unit="mm", coordSystem="data", vpos="center")
        x, y = bar.text.get_position()
        assert x == pytest.approx(5)
        assert y == pytest.approx(4)
        assert bar.text.get_verticalalignment() == "center"
        assert bar.text.get_horizontalalignment() == "center"

    def test_horizontal_bar_has_a_gap_around_the_text(self, panel):
        bar = ScaleBar(panel, (2, 4), 6, unit="mm", coordSystem="data", vpos="center")
        (_, left_end), (right_start, _) = segments(bar)
        text_x0, _, text_x1, _ = text_extent_data(bar)
        assert left_end <= text_x0
        assert right_start >= text_x1
        # the gap is centred on the bar
        assert (left_end + right_start) / 2 == pytest.approx(5)

    def test_horizontal_bar_ends_stay_where_they_were(self, panel):
        bar = ScaleBar(panel, (2, 4), 6, unit="mm", coordSystem="data", vpos="center")
        (start, _), (_, end) = segments(bar)
        assert start == pytest.approx(2)
        assert end == pytest.approx(8)
        _, y = line_xy(bar)
        assert [v for v in y if not np.isnan(v)] == pytest.approx([4, 4, 4, 4])

    def test_vertical_text_is_on_the_bar(self, panel):
        bar = ScaleBar(
            panel,
            (3, 1),
            6,
            unit="mm",
            coordSystem="data",
            orientation="v",
            hpos="center",
        )
        x, y = bar.text.get_position()
        assert x == pytest.approx(3)
        assert y == pytest.approx(4)
        assert bar.text.get_rotation() == 90
        assert bar.text.get_horizontalalignment() == "center"

    def test_vertical_bar_has_a_gap_around_the_text(self, panel):
        bar = ScaleBar(
            panel,
            (3, 0.5),
            6,
            unit="mm",
            coordSystem="data",
            orientation="v",
            hpos="center",
        )
        (_, lower_end), (upper_start, _) = segments(bar)
        _, text_y0, _, text_y1 = text_extent_data(bar)
        assert lower_end <= text_y0
        assert upper_start >= text_y1
        assert (lower_end + upper_start) / 2 == pytest.approx(3.5)

    def test_longer_text_makes_a_longer_gap(self, panel):
        short = ScaleBar(
            panel, (0.5, 4), 9, textstring="1", coordSystem="data", vpos="center"
        )
        long = ScaleBar(
            panel,
            (0.5, 2),
            9,
            textstring="a much longer label",
            coordSystem="data",
            vpos="center",
        )

        def gap(bar):
            (_, end), (start, _) = segments(bar)
            return start - end

        assert gap(long) > gap(short)

    def test_text_wider_than_the_bar_hides_the_bar_with_a_warning(self, panel):
        # zero-length pieces would still draw as dots, so nothing is drawn at all
        with pytest.warns(UserWarning, match="bar is hidden") as record:
            bar = ScaleBar(
                panel,
                (2, 4),
                0.2,
                textstring="much too long for this bar",
                coordSystem="data",
                vpos="center",
            )
        x, y = line_xy(bar)
        assert all(np.isnan(x + y))
        # one warning, blaming this line rather than scilayout internals
        assert len(record) == 1
        assert record[0].filename == __file__

    def test_warning_names_the_text_and_sizes(self, panel):
        with pytest.warns(UserWarning) as record:
            ScaleBar(
                panel,
                (2, 4),
                0.2,
                textstring="too long",
                coordSystem="data",
                vpos="center",
            )
        message = str(record[0].message)
        assert "'too long'" in message
        assert "0.2" in message

    def test_moving_a_hidden_bar_warns_again_at_the_callers_line(self, panel):
        with pytest.warns(UserWarning, match="bar is hidden"):
            bar = ScaleBar(
                panel,
                (2, 4),
                0.2,
                textstring="too long",
                coordSystem="data",
                vpos="center",
            )
        with pytest.warns(UserWarning, match="bar is hidden") as record:
            bar.move(3, 3)
        assert record[0].filename == __file__

    def test_linked_scalebar_warning_points_at_the_caller(self, panel):
        with pytest.warns(UserWarning, match="bar is hidden") as record:
            LinkedScaleBar(
                panel,
                (2, 1),
                0.2,
                0.2,
                x_unit="seconds long",
                coordSystem="data",
                vat="center",
            )
        assert record[0].filename == __file__

    def test_no_warning_when_the_bar_is_long_enough(self, panel):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            ScaleBar(panel, (1, 4), 8, unit="mm", coordSystem="data", vpos="center")

    def test_moving_keeps_the_gap(self, panel):
        bar = ScaleBar(panel, (2, 4), 6, unit="mm", coordSystem="data", vpos="center")
        (_, end), (start, _) = segments(bar)
        bar.move(1, 1)
        (_, new_end), (new_start, _) = segments(bar)
        assert new_start - new_end == pytest.approx(start - end)
        assert (new_end + new_start) / 2 == pytest.approx(4)  # 1 + 6/2

    def test_uncentred_bars_are_not_broken(self, panel):
        bar = ScaleBar(panel, (2, 4), 6, unit="mm", coordSystem="data")
        x, y = line_xy(bar)
        assert not any(np.isnan(x + y))

    def test_centre_is_valid_for_the_text_axis_only(self, panel):
        # 'center' along the bar is the default; across the bar it is opt-in
        ScaleBar(panel, (2, 4), 6, coordSystem="data", vpos="center", hpos="center")
        with pytest.raises(ValueError, match="must be"):
            ScaleBar(panel, (2, 4), 6, coordSystem="data", vpos="middle")

    def test_linked_scalebar_can_centre_text(self, panel):
        linked = LinkedScaleBar(
            panel, (2, 1), 6, 4, coordSystem="data", vat="center", hat="center"
        )
        assert linked.x_scalebar.vpos == "center"
        assert linked.y_scalebar.hpos == "center"
        assert any(np.isnan(line_xy(linked.x_scalebar)[0]))
        assert any(np.isnan(line_xy(linked.y_scalebar)[1]))

    def test_zero_length_bar_is_left_alone(self, panel):
        bar = ScaleBar(
            panel, (2, 4), 0, textstring="0", coordSystem="data", vpos="center"
        )
        x, y = line_xy(bar)
        assert x == pytest.approx([2, 2])
        assert y == pytest.approx([4, 4])


def display_gap_cm(bar: ScaleBar, side: str) -> float:
    """Distance in cm from the centre of the line to the nearest edge of the text.

    Measured in rendered pixels, on the side of the line named by ``side``.
    """
    fig = bar.ax.get_figure()
    renderer = fig.canvas.get_renderer()  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    box = bar.text.get_window_extent(renderer)
    xs, ys = line_xy(bar)
    line_x, line_y = bar.ax.transData.transform((xs[0], ys[0]))
    pixels = {
        "below": line_y - box.y1,
        "above": box.y0 - line_y,
        "left": line_x - box.x1,
        "right": box.x0 - line_x,
    }[side]
    return pixels / fig.dpi * 2.54  # pyright: ignore[reportOptionalMemberAccess]


class TestPadding:
    """Padding is the gap in cm between the edge of the line and the text."""

    def half_line_cm(self, lw: float = 1) -> float:
        return lw / 72 * 2.54 / 2

    @pytest.mark.parametrize(
        ("kwargs", "side"),
        [
            ({"vpos": "bottom"}, "below"),
            ({"vpos": "top"}, "above"),
            ({"orientation": "v", "hpos": "left"}, "left"),
            ({"orientation": "v", "hpos": "right"}, "right"),
        ],
    )
    def test_text_is_pad_cm_from_the_edge_of_the_line(self, panel, kwargs, side):
        bar = ScaleBar(
            panel, (3, 4), 3, unit="mm", coordSystem="data", pad=0.3, **kwargs
        )
        assert display_gap_cm(bar, side) == pytest.approx(
            0.3 + self.half_line_cm(), abs=0.003
        )

    def test_default_pad_comes_from_the_style(self, panel):
        bar = ScaleBar(panel, (3, 4), 3, coordSystem="data")
        assert bar.pad == style.params["scalebars.pad"]

    def test_style_changes_apply_to_new_bars(self, panel):
        style.params["scalebars.pad"] = 0.4
        bar = ScaleBar(panel, (3, 4), 3, unit="mm", coordSystem="data")
        assert bar.pad == 0.4
        assert display_gap_cm(bar, "below") == pytest.approx(
            0.4 + self.half_line_cm(), abs=0.003
        )

    def test_explicit_pad_beats_the_style(self, panel):
        style.params["scalebars.pad"] = 0.4
        bar = ScaleBar(panel, (3, 4), 3, coordSystem="data", pad=0.05)
        assert bar.pad == 0.05

    def test_zero_pad_puts_the_text_against_the_line(self, panel):
        bar = ScaleBar(panel, (3, 4), 3, unit="mm", coordSystem="data", pad=0)
        assert display_gap_cm(bar, "below") == pytest.approx(
            self.half_line_cm(), abs=0.003
        )

    def test_negative_pad_raises(self, panel):
        with pytest.raises(ValueError, match="pad must not be negative"):
            ScaleBar(panel, (3, 4), 3, coordSystem="data", pad=-0.1)

    def test_thicker_lines_push_the_text_away(self, panel):
        thin = ScaleBar(panel, (3, 4), 3, unit="mm", coordSystem="data", pad=0.1, lw=1)
        thick = ScaleBar(panel, (3, 1), 3, unit="mm", coordSystem="data", pad=0.1, lw=8)
        difference = display_gap_cm(thick, "below") - display_gap_cm(thin, "below")
        assert difference == pytest.approx(7 / 72 * 2.54 / 2, abs=0.003)

    def test_pad_does_not_depend_on_the_text(self, panel):
        short = ScaleBar(
            panel, (3, 4), 3, orientation="v", textstring="1", coordSystem="data"
        )
        long = ScaleBar(
            panel,
            (6, 4),
            3,
            orientation="v",
            textstring="a much longer label",
            coordSystem="data",
        )
        assert display_gap_cm(long, "left") == pytest.approx(
            display_gap_cm(short, "left"), abs=0.003
        )

    def test_pad_does_not_depend_on_the_font_size(self, panel):
        small = ScaleBar(
            panel, (3, 4), 3, textstring="1", coordSystem="data", fontsize=6
        )
        large = ScaleBar(
            panel, (3, 1), 3, textstring="1", coordSystem="data", fontsize=16
        )
        assert display_gap_cm(large, "below") == pytest.approx(
            display_gap_cm(small, "below"), abs=0.003
        )

    def test_changing_pad_then_moving_updates_the_text(self, panel):
        bar = ScaleBar(panel, (3, 4), 3, unit="mm", coordSystem="data", pad=0.1)
        before = display_gap_cm(bar, "below")
        bar.pad = 0.5
        bar.move(3, 4)
        assert display_gap_cm(bar, "below") - before == pytest.approx(0.4, abs=0.003)

    def test_works_on_an_inverted_axis(self, panel):
        panel.invert_yaxis()
        bar = ScaleBar(
            panel, (3, 4), 3, unit="mm", coordSystem="data", pad=0.3, vpos="bottom"
        )
        # still below the line on the page, even though larger y is now lower down
        assert display_gap_cm(bar, "below") == pytest.approx(
            0.3 + self.half_line_cm(), abs=0.003
        )

    def test_linked_scalebar_passes_pad_to_both_bars(self, panel):
        linked = LinkedScaleBar(
            panel, (3, 4), 3, 3, x_unit="s", y_unit="mV", coordSystem="data", pad=0.25
        )
        assert linked.x_scalebar.pad == 0.25
        assert linked.y_scalebar.pad == 0.25
        assert display_gap_cm(linked.x_scalebar, "below") == pytest.approx(
            0.25 + self.half_line_cm(), abs=0.003
        )
        assert display_gap_cm(linked.y_scalebar, "left") == pytest.approx(
            0.25 + self.half_line_cm(), abs=0.003
        )


class TestCentredGapPadding:
    def visible_gap_cm(self, bar: ScaleBar) -> float:
        """Gap between the two halves of the line, after the line caps are drawn."""
        (_, left_end), (right_start, _) = segments(bar)
        xs = bar.ax.transData.transform([(left_end, 0), (right_start, 0)])[:, 0]
        fig = bar.ax.get_figure()
        pixels = xs[1] - xs[0] - bar.line.get_linewidth() / 72 * fig.dpi  # pyright: ignore[reportOptionalMemberAccess]
        return pixels / fig.dpi * 2.54  # pyright: ignore[reportOptionalMemberAccess]

    def text_width_cm(self, bar: ScaleBar) -> float:
        fig = bar.ax.get_figure()
        renderer = fig.canvas.get_renderer()  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        return bar.text.get_window_extent(renderer).width / fig.dpi * 2.54  # pyright: ignore[reportOptionalMemberAccess]

    @pytest.mark.parametrize("pad", [0, 0.1, 0.3])
    def test_space_between_text_and_bar_is_pad(self, panel, pad):
        bar = ScaleBar(
            panel,
            (0.5, 4),
            9,
            unit="mm",
            coordSystem="data",
            vpos="center",
            pad=pad,
        )
        assert self.visible_gap_cm(bar) == pytest.approx(
            self.text_width_cm(bar) + 2 * pad, abs=0.005
        )

    def test_thick_lines_keep_the_same_visible_gap(self, panel):
        thin = ScaleBar(
            panel, (0.5, 4), 9, unit="mm", coordSystem="data", vpos="center", lw=1
        )
        thick = ScaleBar(
            panel, (0.5, 2), 9, unit="mm", coordSystem="data", vpos="center", lw=6
        )
        assert self.visible_gap_cm(thick) == pytest.approx(
            self.visible_gap_cm(thin), abs=0.005
        )
