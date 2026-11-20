import warnings
from collections.abc import Generator

import pytest

from scilayout.classes import PanelAxes, SciFigure
from scilayout.locations import resolve_method, to_extent
from scilayout.types import Bound, Extent


@pytest.fixture
def fig() -> Generator[SciFigure, None, None]:
    scifig = SciFigure(figsize=(6, 4))
    yield scifig
    scifig.close()


class TestResolveMethod:
    @pytest.mark.parametrize("method", ["bounds", "extent"])
    def test_valid_methods_do_not_warn(self, method):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert resolve_method(method) == method

    def test_none_warns_and_means_extent(self):
        with pytest.warns(FutureWarning, match="default"):
            assert resolve_method(None) == "extent"

    @pytest.mark.parametrize(
        ("old", "new"),
        [("size", "bounds"), ("bbox", "extent")],
    )
    def test_deprecated_names(self, old, new):
        with pytest.warns(FutureWarning, match=f"'{new}'"):
            assert resolve_method(old) == new

    def test_the_default_warning_names_version_1_0(self):
        with pytest.warns(FutureWarning, match="scilayout 1.0"):
            resolve_method(None)

    @pytest.mark.parametrize("old", ["size", "bbox"])
    def test_deprecated_names_warn_they_go_in_version_1_0(self, old):
        with pytest.warns(FutureWarning, match="removed in scilayout 1.0"):
            resolve_method(old)

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="method must be"):
            resolve_method("fraction")


class TestToExtent:
    def test_bounds(self):
        assert to_extent((1, 2, 3, 4), "bounds") == Extent(1, 2, 4, 6)

    def test_extent(self):
        assert to_extent((1, 2, 3, 4), "extent") == Extent(1, 2, 3, 4)

    def test_returns_extent_type(self):
        assert isinstance(to_extent((1, 2, 3, 4), "bounds"), Extent)

    def test_typed_instances_ignore_method(self):
        assert to_extent(Bound(1, 2, 3, 4), "extent") == Extent(1, 2, 4, 6)
        assert to_extent(Extent(1, 2, 3, 4), "bounds") == Extent(1, 2, 3, 4)

    @pytest.mark.parametrize("location", [(1, 2, 3), (1, 2, 3, 4, 5)])
    def test_wrong_length_raises(self, location):
        with pytest.raises(ValueError, match="4 values"):
            to_extent(location, "extent")

    @pytest.mark.parametrize("location", [(1, 2, -3, 4), (1, 2, 3, -4)])
    @pytest.mark.parametrize("make", [tuple, Bound._make])
    def test_negative_size_raises(self, location, make):
        with pytest.raises(ValueError, match="non-negative"):
            to_extent(make(location), "bounds")

    def test_misordered_extent_raises(self):
        with pytest.raises(ValueError, match="order"):
            to_extent((5, 5, 1, 1), "extent")


class TestPanelMethods:
    def test_bounds_and_extent_give_same_panel(self, fig):
        a = fig.add_panel((1, 2, 3, 4), method="bounds")
        b = fig.add_panel((1, 2, 4, 6), method="extent")
        assert a.get_location() == pytest.approx(b.get_location())
        assert a.get_location() == pytest.approx((1, 2, 4, 6))

    def test_get_location_returns_extent(self, fig):
        panel = fig.add_panel((1, 2, 3, 4), method="bounds")
        assert isinstance(panel.get_location(), Extent)

    def test_add_panel_without_method_warns_and_uses_extent(self, fig):
        with pytest.warns(FutureWarning, match="default") as record:
            panel = fig.add_panel((1, 2, 4, 6))
        assert len(record) == 1
        assert record[0].filename == __file__
        assert panel.get_location() == pytest.approx((1, 2, 4, 6))

    def test_set_location_without_method_warns(self, fig):
        panel = fig.add_panel((1, 2, 4, 6), method="extent")
        with pytest.warns(FutureWarning, match="default") as record:
            panel.set_location((2, 2, 5, 6))
        assert record[0].filename == __file__
        assert panel.get_location() == pytest.approx((2, 2, 5, 6))

    def test_panelaxes_direct_without_method_warns(self, fig):
        with pytest.warns(FutureWarning, match="default") as record:
            PanelAxes(fig, (1, 2, 4, 6))
        assert record[0].filename == __file__

    @pytest.mark.parametrize(("old", "new"), [("size", "bounds"), ("bbox", "extent")])
    def test_deprecated_method_names_still_work(self, fig, old, new):
        with pytest.warns(FutureWarning, match="deprecated") as record:
            old_panel = fig.add_panel((1, 2, 3, 4), method=old)
        assert len(record) == 1
        new_panel = fig.add_panel((1, 2, 3, 4), method=new)
        assert old_panel.get_location() == pytest.approx(new_panel.get_location())

    def test_explicit_method_does_not_warn(self, fig):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            fig.add_panel((1, 2, 3, 4), method="bounds")

    def test_unknown_method_raises(self, fig):
        with pytest.raises(ValueError, match="method must be"):
            fig.add_panel((1, 2, 3, 4), method="fraction")

    def test_wrong_length_raises(self, fig):
        with pytest.raises(ValueError, match="4 values"):
            fig.add_panel((1, 2, 3), method="bounds")  # pyright: ignore[reportArgumentType]

    def test_typed_instance_dispatches_on_type(self, fig):
        panel = fig.add_panel(Bound(1, 2, 3, 4), method="extent")
        assert panel.get_location() == pytest.approx((1, 2, 4, 6))
