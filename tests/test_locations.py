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
