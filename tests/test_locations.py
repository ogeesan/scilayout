from collections.abc import Generator

import numpy as np
import pytest
from matplotlib.figure import Figure
from matplotlib.pyplot import close

from scilayout.locations import (
    CMTransform,
    cm_to_fraction,
    cm_to_inch,
    fraction_to_cm,
    inch_to_cm,
    locationcm_to_position,
)

places = 7


@pytest.fixture
def fig() -> Generator[Figure, None, None]:
    fig_object = Figure(figsize=(6, 4))
    yield fig_object
    close(fig_object)


class TestLocationToPosition:
    def test_location_to_position_positive_values(self, fig):
        location = (1, 2, 5, 3)
        expected_result = (
            0.06561679790026247,
            0.7047244094488189,
            0.26246719160104987,
            0.09842519685039364,
        )
        result = locationcm_to_position(fig, location)
        for res, exp in zip(result, expected_result, strict=True):
            assert res == pytest.approx(exp)

    def test_location_to_position_negative_values(self, fig):
        location = (-2, -3, -1, -1)
        expected_result = (
            -0.13123359580052493,
            1.0984251968503937,
            0.06561679790026247,
            0.19685039370078727,
        )
        result = locationcm_to_position(fig, location)
        for res, exp in zip(result, expected_result, strict=True):
            assert res == pytest.approx(exp)

    def test_location_to_position_zero_values(self, fig):
        location = (0, 0, 0, 0)
        expected_result = (0.0, 1.0, 0.0, 0.0)
        result = locationcm_to_position(fig, location)
        for res, exp in zip(result, expected_result, strict=True):
            assert res == pytest.approx(exp)

    def test_location_to_position_different_values(self, fig):
        location = (2, 1, 6, 4)
        expected_result = (
            0.13123359580052493,
            0.6062992125984252,
            0.2624671916010498,
            0.295275590551181,
        )
        result = locationcm_to_position(fig, location)
        for res, exp in zip(result, expected_result, strict=True):
            assert res == pytest.approx(exp)


class TestConversions:
    def test_cm_inch_round_trip(self):

        assert cm_to_inch(2.54) == pytest.approx(1)
        assert inch_to_cm(1) == pytest.approx(2.54)
        assert inch_to_cm(cm_to_inch(7.3)) == pytest.approx(7.3)

    def test_arrays_are_converted_elementwise(self):

        assert cm_to_inch(np.array([2.54, 5.08])) == pytest.approx([1, 2])

    def test_cm_to_fraction_origin_is_upper_left_to_lower_left(self, fig):

        # figure is 6 x 4 inches = 15.24 x 10.16 cm
        assert cm_to_fraction(fig, (0, 0)) == pytest.approx((0, 1))
        assert cm_to_fraction(fig, (15.24, 10.16)) == pytest.approx((1, 0))

    def test_fraction_cm_round_trip(self, fig):

        assert fraction_to_cm(fig, cm_to_fraction(fig, (3, 4))) == pytest.approx((3, 4))


class TestCMTransform:
    def test_transform_and_inverse(self, fig):

        transform = CMTransform(fig)
        points = np.array([[0, 0], [15.24, 10.16], [3, 4]])
        fractions = transform.transform(points)
        assert fractions[0] == pytest.approx([0, 1])
        assert fractions[1] == pytest.approx([1, 0])
        assert transform.inverted().transform(fractions) == pytest.approx(points)

    def test_old_name_of_the_inverse_is_deprecated(self, fig):
        from scilayout import locations

        with pytest.warns(FutureWarning, match=r"CMTransform\(fig\).inverted\(\)"):
            old = locations.InvertedCMTransform
        assert isinstance(CMTransform(fig).inverted(), old)
        with pytest.raises(AttributeError):
            locations.NoSuchThing  # noqa: B018

    def test_inverse_of_inverse(self, fig):
        transform = CMTransform(fig)
        assert isinstance(transform.inverted().inverted(), CMTransform)

    def test_position_helper_agrees_with_transform(self, fig):
        left, bottom, width, height = locationcm_to_position(fig, (1, 1, 3, 4))
        assert (left, bottom + height) == pytest.approx(
            tuple(CMTransform(fig).transform((1, 1)))
        )
        assert width > 0
        assert height > 0


class TestLocationCmToPosition:
    @pytest.mark.parametrize("corners", [(5, 1, 1, 4), (1, 5, 4, 1)])
    def test_misordered_corners_raise(self, fig, corners):
        with pytest.raises(ValueError, match="less than"):
            locationcm_to_position(fig, corners)


class TestPrecision:
    @pytest.mark.parametrize("value", [0.5, 1, 2.54, 7.3, 13.123456789, 100])
    def test_cm_inch_round_trip_is_exact_to_float_noise(self, value):
        assert inch_to_cm(cm_to_inch(value)) == pytest.approx(value, abs=1e-12)
        assert cm_to_inch(inch_to_cm(value)) == pytest.approx(value, abs=1e-12)

    def test_cm_fraction_round_trip_is_exact_to_float_noise(self, fig):
        for xy in [(0.5, 0.5), (3.3, 4.7), (15.0, 10.0)]:
            back = fraction_to_cm(fig, cm_to_fraction(fig, xy))
            assert back == pytest.approx(xy, abs=1e-12)


class TestCMTransformComposition:
    """The transform combines with matplotlib's own transforms and follows the figure."""

    def test_composes_with_transfigure(self, fig):
        cm = CMTransform(fig)
        composite = cm + fig.transFigure
        points = np.array([[0, 0], [3, 4], [15.24, 10.16]])
        expected = fig.transFigure.transform(cm.transform(points))
        assert composite.transform(points) == pytest.approx(expected)
        # the upper left of the figure is the top of the window
        assert composite.transform((0, 0)) == pytest.approx((0, fig.bbox.height))

    def test_places_text(self, fig):
        text = fig.text(3, 4, "x", transform=CMTransform(fig) + fig.transFigure)
        fig.canvas.draw()
        x, y = text.get_transform().transform(text.get_position())
        assert x / fig.bbox.width == pytest.approx(3 / 15.24)
        assert y / fig.bbox.height == pytest.approx(1 - 4 / 10.16)

    def test_follows_a_resize(self, fig):
        cm = CMTransform(fig)
        composite = cm + fig.transFigure
        before = composite.transform((3, 4))
        fig.set_size_inches(12, 8)
        # 3 cm from the left and 4 cm from the top, whatever the size
        assert composite.transform((3, 4)) == pytest.approx(
            (3 / 2.54 * fig.dpi, fig.bbox.height - 4 / 2.54 * fig.dpi)
        )
        assert cm.transform((15.24, 10.16)) == pytest.approx((0.5, 0.5))
        assert not np.allclose(before, composite.transform((3, 4)))

    def test_follows_a_dpi_change(self, fig):
        composite = CMTransform(fig) + fig.transFigure
        fig.set_dpi(200)
        assert composite.transform((2.54, 0)) == pytest.approx((200, fig.bbox.height))

    def test_inverse_of_composite(self, fig):
        composite = CMTransform(fig) + fig.transFigure
        points = np.array([[1, 2], [7.5, 3.25]])
        assert composite.inverted().transform(composite.transform(points)) == (
            pytest.approx(points)
        )

    def test_inverted_transform_composes_too(self, fig):
        to_cm = fig.transFigure.inverted() + CMTransform(fig).inverted()
        assert to_cm.transform((fig.bbox.width, 0)) == pytest.approx((15.24, 10.16))

    def test_single_points_and_arrays(self, fig):
        cm = CMTransform(fig)
        assert cm.transform((0, 0)).shape == (2,)
        assert cm.transform([[0, 0], [1, 1]]).shape == (2, 2)
