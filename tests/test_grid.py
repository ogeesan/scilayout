import pytest

from scilayout.grid import GuideGridClass


@pytest.fixture
def grid(scifig) -> GuideGridClass:
    return scifig.grid


class TestGridInit:
    def test_figure_has_a_grid_that_starts_hidden(self, scifig, grid):
        assert isinstance(grid, GuideGridClass)
        assert grid.figure is scifig
        assert grid.ax is None

    def test_default_parameters(self, grid):
        assert grid.major_interval == 5
        assert grid.minor_interval == 1
        assert grid.half_spacer is True

    def test_custom_parameters(self, scifig):
        grid = GuideGridClass(scifig, major_interval=2, minor_interval=0.5)
        assert grid.major_interval == 2
        assert grid.minor_interval == 0.5


class TestGridDrawing:
    def test_show_creates_axes_spanning_the_figure_in_cm(self, scifig, grid):
        grid.show()
        assert grid.ax is not None
        assert grid.ax.get_visible()
        assert grid.ax.get_xlim() == pytest.approx((0, 13))
        # y is inverted so the origin is the upper left
        assert grid.ax.get_ylim() == pytest.approx((10, 0))

    def test_grid_axes_is_not_navigable(self, grid):
        grid.show()
        assert grid.ax is not None
        assert not grid.ax.get_navigate()

    def test_markers_drawn(self, grid):
        grid.show()
        assert grid.minor_scatter is not None
        assert grid.half_scatter is not None
        assert grid.major_scatter is not None

    def test_major_markers_every_major_interval(self, grid):
        grid.show()
        assert grid.major_scatter is not None
        offsets = grid.major_scatter.get_offsets()
        assert sorted({float(x) for x, _ in offsets}) == [0, 5, 10]
        assert sorted({float(y) for _, y in offsets}) == [0, 5, 10]

    def test_no_half_markers_when_disabled(self, scifig):
        grid = GuideGridClass(scifig, half_spacer=False)
        grid.redraw()
        assert grid.half_scatter is None

    def test_redraw_does_not_add_axes(self, scifig, grid):
        grid.show()
        count = len(scifig.axes)
        grid.redraw()
        assert len(scifig.axes) == count

    def test_hide_and_show(self, grid):
        grid.show()
        grid.hide()
        assert grid.ax is not None
        assert not grid.ax.get_visible()
        grid.show()
        assert grid.ax.get_visible()

    def test_hide_before_showing_does_nothing(self, grid):
        grid.hide()
        assert grid.ax is None

    def test_redraw_follows_figure_size(self, scifig, grid):
        grid.show()
        scifig.set_size_cm(20, 8)
        grid.redraw()
        assert grid.ax is not None
        assert grid.ax.get_xlim() == pytest.approx((0, 20))
        assert grid.ax.get_ylim() == pytest.approx((8, 0))

    def test_remove_detaches_axes(self, grid):
        grid.show()
        grid.remove()
        assert grid.ax is None


class TestGridParameters:
    def test_changed_intervals_apply_on_redraw(self, grid):
        grid.show()
        grid.major_interval = 10
        grid.redraw()
        assert grid.major_scatter is not None
        offsets = grid.major_scatter.get_offsets()
        assert sorted({float(x) for x, _ in offsets}) == [0, 10]


class TestGridLines:
    def test_add_line(self, grid):
        grid.add_line("x", 3)
        assert 3 in grid.lines["x"]
        assert grid.ax is not None
        assert len(grid.ax.lines) == 1

    def test_add_lines_on_both_axes(self, grid):
        grid.add_line("x", 3)
        grid.add_line("y", 4)
        assert grid.ax is not None
        assert len(grid.ax.lines) == 2

    def test_invalid_axis_raises(self, grid):
        with pytest.raises(ValueError, match="'x' or 'y'"):
            grid.add_line("z", 3)

    def test_clear_lines(self, grid):
        grid.add_line("x", 3)
        grid.clear_lines()
        assert grid.lines == {"x": {}, "y": {}}
        assert grid.ax is not None
        assert len(grid.ax.lines) == 0


class TestSciFigureGridIntegration:
    def test_draw_grid_shows_the_grid(self, scifig):
        scifig.draw_grid()
        assert scifig.grid.ax is not None
        assert scifig.grid.ax.get_visible()

    def test_draw_grid_twice_reuses_axes(self, scifig):
        scifig.draw_grid()
        count = len(scifig.axes)
        scifig.draw_grid()
        assert len(scifig.axes) == count

    def test_draw_grid_with_settings_warns_not_implemented(self, scifig, capsys):
        with pytest.warns(UserWarning, match="not implemented") as record:
            scifig.draw_grid(major_interval=2)
        assert record[0].filename == __file__
        assert capsys.readouterr().out == ""

    def test_clear_detaches_grid(self, scifig):
        scifig.draw_grid()
        scifig.clear()
        assert scifig.grid.ax is None
        assert len(scifig.axes) == 0

    def test_grid_can_be_drawn_again_after_clear(self, scifig):
        scifig.draw_grid()
        scifig.clear()
        scifig.draw_grid()
        assert scifig.grid.ax is not None
        assert scifig.grid.ax.get_visible()
