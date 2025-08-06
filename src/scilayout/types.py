"""Type definitions for scilayout."""

from typing import NamedTuple

centimetres = float
"""A type alias for centimeters, used for positions and dimensions in figures."""
inches = float
"""A type alias for inches, used for positions and dimensions in figures."""
fraction = float
"""A type alias for figure fraction, used for positions and dimensions in figures."""


class Extent(NamedTuple):
    """A named tuple to hold extent (position) coordinates."""

    x0: float
    y0: float
    x1: float
    y1: float


class Bound(NamedTuple):
    """A named tuple to hold bounding box (width, height) coordinates."""

    x: float
    y: float
    w: float
    h: float


class ExtentCM(Extent):
    """A named tuple to hold extent (position) coordinates."""

    x0: centimetres
    y0: centimetres
    x1: centimetres
    y1: centimetres


class BoundCM(Bound):
    """A named tuple to hold bounding box (width, height) coordinates."""

    x: centimetres
    y: centimetres
    w: centimetres
    h: centimetres


class ExtentInches(Extent):
    """A named tuple to hold extent (position) coordinates in inches."""

    x0: inches
    y0: inches
    x1: inches
    y1: inches


class BoundInches(Bound):
    """A named tuple to hold bounding box (width, height) coordinates in inches."""

    x: inches
    y: inches
    w: inches
    h: inches


class ExtentFraction(Extent):
    """A named tuple to hold extent (position) coordinates in figure fraction."""

    x0: fraction
    y0: fraction
    x1: fraction
    y1: fraction
