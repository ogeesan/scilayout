"""Lock in the public location API.

If one of these fails, a public behaviour has changed: check it is intentional and
that the deprecation story (see ``scilayout.locations.resolve_method``) still holds.
"""

import inspect
import warnings
from collections.abc import Generator

import pytest

import scilayout
from scilayout.classes import PanelAxes, SciFigure
from scilayout.types import Extent


@pytest.fixture
def fig() -> Generator[SciFigure, None, None]:
    scifig = scilayout.figure(figsize=(6, 4))
    yield scifig
    scifig.close()


class TestEntryPoints:
    def test_figure_returns_scifigure(self, fig):
        assert isinstance(fig, SciFigure)

    def test_add_panel_returns_panelaxes(self, fig):
        assert isinstance(fig.add_panel((1, 1, 2, 2), method="bounds"), PanelAxes)

    @pytest.mark.parametrize("func", [SciFigure.add_panel, PanelAxes.set_location])
    def test_method_is_optional_and_defaults_to_none(self, func):
        # None is what triggers the default-change warning, so it must stay None
        # until the default is deliberately flipped.
        assert inspect.signature(func).parameters["method"].default is None

    def test_add_panel_positional_order(self):
        params = list(inspect.signature(SciFigure.add_panel).parameters)
        assert params[:4] == ["self", "location", "panellabel", "method"]


class TestDefaultInterpretation:
    """A bare tuple means (x0, y0, x1, y1) for now, and warns that it will change."""

    def test_default_is_extent_with_future_warning(self, fig):
        with pytest.warns(FutureWarning, match="changing from 'extent'"):
            panel = fig.add_panel((1, 2, 5, 6))
        assert panel.get_location() == pytest.approx((1, 2, 5, 6))

    def test_future_default_is_announced(self, fig):
        with pytest.warns(FutureWarning, match="'bounds'"):
            fig.add_panel((1, 2, 5, 6))


class TestMethods:
    def test_bounds_is_x_y_width_height(self, fig):
        panel = fig.add_panel((1, 2, 5, 6), method="bounds")
        assert panel.get_location() == pytest.approx((1, 2, 6, 8))

    def test_extent_is_corners(self, fig):
        panel = fig.add_panel((1, 2, 5, 6), method="extent")
        assert panel.get_location() == pytest.approx((1, 2, 5, 6))

    @pytest.mark.parametrize(
        ("old", "new"),
        [("size", "bounds"), ("bbox", "extent")],
    )
    def test_old_names_are_deprecated_aliases(self, fig, old, new):
        with pytest.warns(FutureWarning, match="deprecated"):
            old_panel = fig.add_panel((1, 2, 5, 6), method=old)
        new_panel = fig.add_panel((1, 2, 5, 6), method=new)
        assert old_panel.get_location() == pytest.approx(new_panel.get_location())

    def test_explicit_methods_never_warn(self, fig):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            fig.add_panel((1, 2, 5, 6), method="bounds").set_location(
                (1, 2, 5, 6), method="extent"
            )

    @pytest.mark.parametrize("container", [tuple, list])
    def test_sequences_are_accepted(self, fig, container):
        panel = fig.add_panel(container((1, 2, 5, 6)), method="extent")
        assert panel.get_location() == pytest.approx((1, 2, 5, 6))


class TestGetLocation:
    def test_returns_extent_named_tuple(self, fig):
        location = fig.add_panel((1, 2, 5, 6), method="extent").get_location()
        assert isinstance(location, Extent)
        assert isinstance(location, tuple)
        assert location._fields == ("x0", "y0", "x1", "y1")

    def test_unpacks_like_a_tuple(self, fig):
        x0, y0, x1, y1 = fig.add_panel((1, 2, 5, 6), method="extent").get_location()
        assert (x0, y0, x1, y1) == pytest.approx((1, 2, 5, 6))

    def test_values_are_plain_floats(self, fig):
        location = fig.add_panel((1, 2, 5, 6), method="extent").get_location()
        assert all(type(value) is float for value in location)

    @pytest.mark.parametrize("method", ["bounds", "extent"])
    def test_set_then_get_round_trips(self, fig, method):
        panel = fig.add_panel((0, 0, 1, 1), method="extent")
        panel.set_location((2, 3, 6, 7), method=method)
        expected = (2, 3, 8, 10) if method == "bounds" else (2, 3, 6, 7)
        assert panel.get_location() == pytest.approx(expected)
