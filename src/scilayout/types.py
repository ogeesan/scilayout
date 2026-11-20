"""Type definitions for scilayout."""

from dataclasses import dataclass
from typing import NamedTuple

centimetres = float
"""A type alias for centimeters, used for positions and dimensions in figures."""
inches = float
"""A type alias for inches, used for positions and dimensions in figures."""
fraction = float
"""A type alias for figure fraction, used for positions and dimensions in figures."""


@dataclass
class Extent(NamedTuple):
    """A named tuple to hold extent (positions of corners) coordinates."""

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        """Ensure that the coordinates are in the correct order."""
        if not all(
            isinstance(coord, (int, float))
            for coord in (self.x0, self.y0, self.x1, self.y1)
        ):
            msg = "Coordinates must be numeric (int or float)."
            raise TypeError(msg)

        if self.x0 > self.x1 or self.y0 > self.y1:
            msg = "Coordinates must be in the order: (x0, y0, x1, y1)."
            raise ValueError(msg)


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
