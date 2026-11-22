"""Types for locations on a figure.

Rectangles are described either by their corners, an [`Extent`][scilayout.types.Extent]
(``x0, y0, x1, y1``), or by their origin and size, a [`Bound`][scilayout.types.Bound]
(``x, y, w, h``). The ``...CM``, ``...Inches`` and ``...Fraction`` names are aliases that
say which unit is meant. They are the same classes, so the unit is documentation only.
For cm the origin is the upper left of the figure.
"""

from numbers import Real
from typing import NamedTuple

from pydantic import BaseModel

__all__ = [
    "Bound",
    "BoundCM",
    "BoundFraction",
    "BoundInches",
    "Extent",
    "ExtentCM",
    "ExtentFraction",
    "ExtentInches",
    "centimetres",
    "fraction",
    "inches",
]

centimetres = float
"""A type alias for centimeters, used for positions and dimensions in figures."""
inches = float
"""A type alias for inches, used for positions and dimensions in figures."""
fraction = float
"""A type alias for figure fraction, used for positions and dimensions in figures."""


class BoundsModel(BaseModel):
    """A pydantic model for bounds (x, y, w, h) in cm.

    This is used for validating bounds passed as a dictionary.
    """

    x: float
    y: float
    width: float
    height: float


class ExtentModel(BaseModel):
    """A pydantic model for extent (x0, y0, x1, y1) in cm.

    This is used for validating extent passed as a dictionary.
    """

    x0: float
    y0: float
    x1: float
    y1: float


Models = BoundsModel | ExtentModel


class _ExtentFields(NamedTuple):
    x0: float
    y0: float
    x1: float
    y1: float


class Extent(_ExtentFields):
    """Extent of a rectangle given by its corners (x0, y0, x1, y1).

    An immutable 4-tuple with named fields, checked on creation: all values must be
    real numbers, ``x0 <= x1`` and ``y0 <= y1``. Note that ``_replace`` does not
    repeat the checks.

    Attributes
    ----------
    x0, y0 : float
        One corner (the upper left, for locations in cm).
    x1, y1 : float
        The opposite corner.

    Examples
    --------
    >>> extent = Extent(1, 2, 5, 6)
    >>> extent.x1
    5
    >>> x0, y0, x1, y1 = extent
    >>> Extent(5, 0, 1, 1)
    Traceback (most recent call last):
        ...
    ValueError: Coordinates must be in the order: (x0, y0, x1, y1).

    """

    __slots__ = ()

    def __new__(cls, x0: float, y0: float, x1: float, y1: float) -> "Extent":
        """Create an Extent, checking the coordinates are numeric and ordered.

        Parameters
        ----------
        x0, y0 : float
            One corner.
        x1, y1 : float
            The opposite corner.

        Raises
        ------
        TypeError
            If a coordinate is not a real number.
        ValueError
            If ``x0 > x1`` or ``y0 > y1``.

        """
        if not all(isinstance(c, Real) for c in (x0, y0, x1, y1)):
            msg = "Coordinates must be numeric (int or float)."
            raise TypeError(msg)
        if x0 > x1 or y0 > y1:
            msg = "Coordinates must be in the order: (x0, y0, x1, y1)."
            raise ValueError(msg)
        return super().__new__(cls, x0, y0, x1, y1)

    def to_bound(self) -> "Bound":
        """Convert to a [`Bound`][scilayout.types.Bound] (origin and size)."""
        return Bound(self.x0, self.y0, self.x1 - self.x0, self.y1 - self.y0)


class Bound(NamedTuple):
    """Rectangle given by its origin and size (x, y, w, h).

    An immutable 4-tuple with named fields. Unlike [`Extent`][scilayout.types.Extent] it is not checked
    on creation.

    Attributes
    ----------
    x, y : float
        The origin (the upper left, for locations in cm).
    w, h : float
        Width and height.

    Examples
    --------
    >>> bound = Bound(1, 2, 4, 4)
    >>> bound.w
    4

    """

    x: float
    y: float
    w: float
    h: float

    def to_extent(self) -> Extent:
        """Convert to an [`Extent`][scilayout.types.Extent] (corners)."""
        return Extent(self.x, self.y, self.x + self.w, self.y + self.h)


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
