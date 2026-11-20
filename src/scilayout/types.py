"""Type definitions for scilayout."""

from numbers import Real
from typing import NamedTuple

centimetres = float
"""A type alias for centimeters, used for positions and dimensions in figures."""
inches = float
"""A type alias for inches, used for positions and dimensions in figures."""
fraction = float
"""A type alias for figure fraction, used for positions and dimensions in figures."""


class _ExtentFields(NamedTuple):
    x0: float
    y0: float
    x1: float
    y1: float


class Extent(_ExtentFields):
    """Extent of a rectangle given by its corners (x0, y0, x1, y1).

    Validated on creation: all values must be real numbers and ``x0 <= x1`` and
    ``y0 <= y1``. Behaves as an immutable 4-tuple with named fields.
    """

    __slots__ = ()

    def __new__(cls, x0: float, y0: float, x1: float, y1: float) -> "Extent":
        """Create an Extent, checking the coordinates are numeric and ordered."""
        if not all(isinstance(c, Real) for c in (x0, y0, x1, y1)):
            msg = "Coordinates must be numeric (int or float)."
            raise TypeError(msg)
        if x0 > x1 or y0 > y1:
            msg = "Coordinates must be in the order: (x0, y0, x1, y1)."
            raise ValueError(msg)
        return super().__new__(cls, x0, y0, x1, y1)


class Bound(NamedTuple):
    """A named tuple to hold bounding box (width, height) coordinates."""

    x: float
    y: float
    w: float
    h: float


ExtentCM = Extent
"""Extent (x0, y0, x1, y1) in centimetres from the upper left of the figure."""
BoundCM = Bound
"""Bound (x, y, w, h) in centimetres from the upper left of the figure."""
ExtentInches = Extent
"""Extent (x0, y0, x1, y1) in inches."""
BoundInches = Bound
"""Bound (x, y, w, h) in inches."""
ExtentFraction = Extent
"""Extent (x0, y0, x1, y1) in figure fraction."""
BoundFraction = Bound
"""Bound (x, y, w, h) in figure fraction."""
