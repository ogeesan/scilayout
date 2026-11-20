import numpy as np
import pytest

from scilayout.types import Bound, Extent, ExtentCM


class TestExtent:
    def test_construct_and_fields(self):
        extent = Extent(1, 2, 5, 6)
        assert (extent.x0, extent.y0, extent.x1, extent.y1) == (1, 2, 5, 6)

    def test_is_tuple(self):
        extent = Extent(1, 2, 5, 6)
        assert isinstance(extent, tuple)
        assert extent == (1, 2, 5, 6)
        x0, y0, x1, y1 = extent
        assert (x0, y0, x1, y1) == (1, 2, 5, 6)

    def test_immutable(self):
        extent = Extent(1, 2, 5, 6)
        with pytest.raises(AttributeError):
            extent.x0 = 0  # pyright: ignore[reportAttributeAccessIssue]

    def test_unit_alias(self):
        assert isinstance(ExtentCM(1, 1, 5, 5), Extent)

    def test_zero_size_allowed(self):
        assert Extent(0, 0, 0, 0) == (0, 0, 0, 0)

    def test_negative_values_allowed(self):
        assert Extent(-2, -3, -1, -1) == (-2, -3, -1, -1)

    def test_numpy_scalars_allowed(self):
        assert Extent(np.float64(1), 2, 5.5, 6) == (1, 2, 5.5, 6)

    @pytest.mark.parametrize("args", [(5, 0, 1, 1), (0, 5, 1, 1)])
    def test_wrong_order_raises(self, args):
        with pytest.raises(ValueError, match="order"):
            Extent(*args)

    @pytest.mark.parametrize("args", [("a", 0, 1, 1), (0, None, 1, 1)])
    def test_non_numeric_raises(self, args):
        with pytest.raises(TypeError, match="numeric"):
            Extent(*args)


class TestBound:
    def test_construct_and_fields(self):
        bound = Bound(1, 2, 3, 4)
        assert (bound.x, bound.y, bound.w, bound.h) == (1, 2, 3, 4)
        assert bound == (1, 2, 3, 4)
