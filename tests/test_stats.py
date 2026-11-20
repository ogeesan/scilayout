import numpy as np
import pytest

from scilayout.stats import StatsLine


class TestStatsLine:
    def test_draws_bar_and_two_drops(self, panel):
        before = len(panel.lines)
        StatsLine(panel, 0.9, 2, 6)
        assert len(panel.lines) == before + 3

    def test_main_bar_coordinates(self, panel):
        line = StatsLine(panel, 0.9, 2, 6)
        assert line.main_bar is not None
        bar = line.main_bar[0]
        assert np.asarray(bar.get_xdata()).tolist() == [2, 6]
        assert np.asarray(bar.get_ydata()).tolist() == [0.9, 0.9]

    def test_drops_hang_below_the_bar(self, panel):
        line = StatsLine(panel, 0.9, 2, 6)
        assert line.left_drop is not None
        assert line.right_drop is not None
        left, right = line.left_drop[0], line.right_drop[0]
        assert np.asarray(left.get_xdata()).tolist() == [2, 2]
        assert np.asarray(right.get_xdata()).tolist() == [6, 6]
        assert np.asarray(left.get_ydata()).tolist() == pytest.approx(
            [0.9, 0.9 - line.drop_amount]
        )
        assert np.asarray(right.get_ydata()).tolist() == pytest.approx(
            [0.9, 0.9 - line.drop_amount]
        )

    def test_axis_limits_are_preserved(self, panel):
        StatsLine(panel, 0.9, 2, 6)
        assert panel.get_xlim() == (0, 10)
        assert panel.get_ylim() == (0, 8)

    def test_lines_are_not_clipped_or_in_legend(self, panel):
        line = StatsLine(panel, 0.9, 2, 6)
        assert line.main_bar is not None
        bar = line.main_bar[0]
        assert not bar.get_clip_on()
        assert bar.get_label() == "_nolegend_"

    def test_draw_replaces_existing_lines(self, panel):
        line = StatsLine(panel, 0.9, 2, 6)
        count = len(panel.lines)
        line.draw()
        assert len(panel.lines) == count

    def test_changing_attributes_then_draw(self, panel):
        line = StatsLine(panel, 0.9, 2, 6)
        line.x1 = 8
        line.color = "red"
        line.linewidth = 3
        line.draw()
        assert line.main_bar is not None
        bar = line.main_bar[0]
        assert np.asarray(bar.get_xdata()).tolist() == [2, 8]
        assert bar.get_color() == "red"
        assert bar.get_linewidth() == 3

    def test_default_transform_is_data_x_axes_y(self, panel):
        line = StatsLine(panel, 0.9, 2, 6)
        assert line.main_bar is not None
        display = line.main_bar[0].get_transform().transform((2, 0.9))
        expected = (
            panel.transData.transform((2, 0))[0],
            panel.transAxes.transform((0, 0.9))[1],
        )
        assert tuple(display) == pytest.approx(expected)

    def test_set_transform_both_data(self, panel):
        line = StatsLine(panel, 4, 2, 6)
        line.set_transform(x="data", y="data")
        assert line.main_bar is not None
        display = line.main_bar[0].get_transform().transform((2, 4))
        assert tuple(display) == pytest.approx(tuple(panel.transData.transform((2, 4))))

    def test_set_transform_both_axes(self, panel):
        line = StatsLine(panel, 0.5, 0.2, 0.6)
        line.set_transform(x="axes", y="axes")
        assert line.main_bar is not None
        display = line.main_bar[0].get_transform().transform((0.2, 0.5))
        assert tuple(display) == pytest.approx(
            tuple(panel.transAxes.transform((0.2, 0.5)))
        )

    def test_set_transform_unknown_raises(self, panel):
        line = StatsLine(panel, 0.9, 2, 6)
        with pytest.raises(ValueError, match="Unknown transform"):
            line.set_transform(x="figure")
