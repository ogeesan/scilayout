from collections.abc import Generator

import pytest
from matplotlib.pyplot import close

import scilayout


@pytest.fixture
def ax() -> Generator[scilayout.classes.PanelAxes, None, None]:
    fig = scilayout.figure()
    testax = fig.add_panel((1, 2, 5, 5), method="bounds")
    yield testax
    close(fig)


@pytest.fixture
def panellabel(ax: scilayout.classes.PanelAxes) -> scilayout.classes.PanelLabel:
    ax.add_label("a")
    assert ax.panellabel is not None
    return ax.panellabel


class TestPanelLabels:
    def test_initial_panel_labels(self, panellabel):
        xoffset = scilayout.style.params["panellabel.xoffset"]
        yoffset = scilayout.style.params["panellabel.yoffset"]
        assert panellabel.xoffset == pytest.approx(xoffset)
        assert panellabel.yoffset == pytest.approx(yoffset)
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(1 + xoffset)
        assert pos[1] == pytest.approx(2 + yoffset)

    def test_panel_reposition(self, ax, panellabel):
        """Test that the label is repositioned when the panel is moved"""
        ax.set_location((2, 3, 6, 6), method="bounds")
        xoffset = scilayout.style.params["panellabel.xoffset"]
        yoffset = scilayout.style.params["panellabel.yoffset"]
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(2 + xoffset)
        assert pos[1] == pytest.approx(3 + yoffset)

    def test_set_location(self, panellabel):
        """Set locations of panel labels manually"""
        # Test x position
        panellabel.set_location(x=3)
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(3)

        # Test y position
        panellabel.set_location(y=4.2)
        pos = panellabel.get_location()
        assert pos[1] == pytest.approx(4.2)

        # Test both x and y location changes
        panellabel.set_location(x=1.5, y=2.5)
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(1.5)
        assert pos[1] == pytest.approx(2.5)


def edges_cm(label: scilayout.classes.PanelLabel) -> tuple[float, float, float, float]:
    """Left, right, top and bottom of the label text in cm from the upper left."""
    fig = label.ax._fig
    renderer = fig.canvas.get_renderer()  # pyright: ignore[reportAttributeAccessIssue]
    box = label.text.get_window_extent(renderer)
    _, height_cm = scilayout.locations.inch_to_cm(fig.get_size_inches())
    scale = 2.54 / fig.dpi
    return (
        box.x0 * scale,
        box.x1 * scale,
        height_cm - box.y1 * scale,
        height_cm - box.y0 * scale,
    )


class TestAlignment:
    """The alignment says which point of the text sits at the label's position."""

    def test_defaults(self, panellabel):
        assert panellabel.text.get_horizontalalignment() == "left"
        assert panellabel.text.get_verticalalignment() == "baseline"

    @pytest.mark.parametrize("h", ["left", "center", "right"])
    @pytest.mark.parametrize("v", ["baseline", "bottom", "center", "top"])
    def test_sets_the_text_alignment(self, panellabel, h, v):
        panellabel.set_alignment(h=h, v=v)
        assert panellabel.text.get_horizontalalignment() == h
        assert panellabel.text.get_verticalalignment() == v

    def test_calling_without_arguments_restores_the_defaults(self, panellabel):
        panellabel.set_alignment(h="right", v="top")
        panellabel.set_alignment()
        assert panellabel.text.get_horizontalalignment() == "left"
        assert panellabel.text.get_verticalalignment() == "baseline"

    def test_does_not_move_the_anchor_or_the_offset(self, panellabel):
        before = (panellabel.get_location(), panellabel.xoffset, panellabel.yoffset)
        panellabel.set_alignment(h="right", v="top")
        assert panellabel.get_location() == pytest.approx(before[0])
        assert (panellabel.xoffset, panellabel.yoffset) == (before[1], before[2])

    def test_left_puts_the_left_edge_at_the_position(self, panellabel):
        left, *_ = edges_cm(panellabel)
        assert left == pytest.approx(panellabel.get_location()[0], abs=0.01)

    def test_right_puts_the_right_edge_at_the_position(self, panellabel):
        panellabel.set_alignment(h="right")
        _, right, *_ = edges_cm(panellabel)
        assert right == pytest.approx(panellabel.get_location()[0], abs=0.01)

    def test_centre_puts_the_middle_at_the_position(self, panellabel):
        panellabel.set_alignment(h="center")
        left, right, *_ = edges_cm(panellabel)
        assert (left + right) / 2 == pytest.approx(
            panellabel.get_location()[0], abs=0.01
        )

    def test_top_puts_the_top_edge_at_the_position(self, panellabel):
        panellabel.set_alignment(v="top")
        _, _, top, _ = edges_cm(panellabel)
        assert top == pytest.approx(panellabel.get_location()[1], abs=0.01)

    def test_bottom_puts_the_bottom_edge_at_the_position(self, panellabel):
        panellabel.set_alignment(v="bottom")
        *_, bottom = edges_cm(panellabel)
        assert bottom == pytest.approx(panellabel.get_location()[1], abs=0.01)

    def test_right_aligned_label_grows_away_from_the_panel(self, ax, panellabel):
        panellabel.set_alignment(h="right")
        _, right, *_ = edges_cm(panellabel)
        panel_left = ax.get_location().x0
        assert right < panel_left

    @pytest.mark.parametrize(("h", "v"), [("middle", "baseline"), ("left", "middle")])
    def test_invalid_alignment_raises(self, panellabel, h, v):
        with pytest.raises(ValueError, match="not a valid value"):
            panellabel.set_alignment(h=h, v=v)  # pyright: ignore[reportArgumentType]

    def test_alignment_survives_moving_the_panel(self, ax, panellabel):
        panellabel.set_alignment(h="right", v="top")
        ax.set_location((3, 4, 5, 5), method="bounds")
        assert panellabel.text.get_horizontalalignment() == "right"
        _, right, top, _ = edges_cm(panellabel)
        x, y = panellabel.get_location()
        assert right == pytest.approx(x, abs=0.01)
        assert top == pytest.approx(y, abs=0.01)
