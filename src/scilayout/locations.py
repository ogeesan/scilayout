"""Convert between cm, inch, and fraction locations in matplotlib figures."""

from __future__ import annotations

import warnings
from typing import Any, Literal, overload

import matplotlib.figure
import numpy as np
from matplotlib.transforms import Transform
from numpy.typing import ArrayLike

from .types import Bound, Extent, ExtentCM, centimetres

LocationMethod = Literal["bounds", "extent"]
"""How to read a 4-tuple location.

- ``"bounds"``: (x, y, width, height)
- ``"extent"``: (x0, y0, x1, y1), the corners
"""

_DEPRECATED_METHODS: dict[str, LocationMethod] = {"size": "bounds", "bbox": "extent"}


def resolve_method(method: str | None, stacklevel: int = 3) -> LocationMethod:
    """Validate a location ``method``, warning about deprecated usage.

    ``None`` (not specifying a method) currently means ``"extent"`` but this will
    change to ``"bounds"``. The old names ``"bbox"`` and ``"size"`` are deprecated
    aliases of ``"extent"`` and ``"bounds"``.

    Parameters
    ----------
    method : str | None
        ``"bounds"``, ``"extent"``, or a deprecated value.
    stacklevel : int
        Passed to ``warnings.warn``. The default points at the caller of the
        function that called this one.

    Returns
    -------
    LocationMethod
        ``"bounds"`` or ``"extent"``.

    """
    if method is None:
        warnings.warn(
            "The default interpretation of a location tuple is changing from "
            "'extent' (x0, y0, x1, y1) to 'bounds' (x, y, width, height) in a "
            "future release. Pass method='extent' to keep the current behaviour, "
            "or method='bounds' to adopt the new one.",
            FutureWarning,
            stacklevel=stacklevel,
        )
        return "extent"
    if method in _DEPRECATED_METHODS:
        new = _DEPRECATED_METHODS[method]
        warnings.warn(
            f"method={method!r} is deprecated, use method={new!r} instead.",
            FutureWarning,
            stacklevel=stacklevel,
        )
        return new
    if method in ("bounds", "extent"):
        return method  # pyright: ignore[reportReturnType]
    msg = f"method must be 'bounds' or 'extent', not {method!r}"
    raise ValueError(msg)


def to_extent(location: tuple[float, ...], method: LocationMethod) -> ExtentCM:
    """Convert a 4-tuple location in cm to an extent (corners).

    A :class:`~scilayout.types.Bound` or :class:`~scilayout.types.Extent` instance
    is interpreted by its type and ``method`` is ignored.

    Parameters
    ----------
    location : tuple[float, float, float, float]
        Location in cm, origin at the upper left of the figure.
    method : LocationMethod
        ``"bounds"`` reads (x, y, w, h), ``"extent"`` reads (x0, y0, x1, y1).

    Returns
    -------
    ExtentCM
        Corners (x0, y0, x1, y1) in cm.

    """
    if isinstance(location, Extent):
        return location
    if len(location) != 4:
        msg = f"location must have 4 values, got {len(location)}"
        raise ValueError(msg)
    if isinstance(location, Bound) or method == "bounds":
        x, y, w, h = location
        if w < 0 or h < 0:
            msg = f"width and height must be non-negative, got ({w}, {h})"
            raise ValueError(msg)
        return ExtentCM(x, y, x + w, y + h)
    return ExtentCM(*location)


def locationcm_to_position(
    fig: matplotlib.figure.Figure,
    location_corners: tuple[centimetres, centimetres, centimetres, centimetres],
) -> tuple[float, float, float, float]:
    """Convert an upper left origin cm extent to figure fraction rect.

    :param fig: Figure window to find true size from
    :type fig: matplotlib.figure.Figure
    :param location_corners: (x1, y1, x2, y2), origin point is upper left of figure (y1 is visual up), cm units
    :type location_corners: Tuple[float, float, float, float]
    :return: (x1, y1, width, height), origin point is lower left of figure (y1 is visual down), fraction units
    :rtype: Tuple[float, float, float, float]
    """
    x0_cm, y0_cm, x1_cm, y1_cm = location_corners
    if x0_cm > x1_cm or y0_cm > y1_cm:
        msg = "x0 must be less than x1 and y0 must be less than y1"
        raise ValueError(msg)

    # Create the transform for centimeter-based positioning
    cm_transform = CMTransform(fig)

    # Transform the (x0_cm, y0_cm) and (x1_cm, y1_cm) positions
    transformed_coords = cm_transform.transform([[x0_cm, y0_cm], [x1_cm, y1_cm]])

    # Extract transformed figure coordinates
    left, top = transformed_coords[0]  # Top-left corner in figure coordinates
    right, bottom = transformed_coords[1]  # Bottom-right corner in figure coordinates

    # Calculate width and height in figure coordinates
    width_figure = right - left
    height_figure = top - bottom

    # Convert into position
    return (
        float(left),
        float(bottom),
        float(width_figure),
        float(height_figure),
    )


# TODO: check precision conversions of integer
# setting to location .5 and back again gives a slight difference
@overload
def cm_to_inch(cm: float) -> float: ...
@overload
def cm_to_inch(cm: np.ndarray) -> np.ndarray: ...
def cm_to_inch(cm: float | np.ndarray) -> float | np.ndarray:
    """Convert centimeters to inches."""
    return cm / 2.54


@overload
def inch_to_cm(inch: float) -> float: ...
@overload
def inch_to_cm(inch: np.ndarray) -> np.ndarray: ...
def inch_to_cm(inch: float | np.ndarray) -> float | np.ndarray:
    """Convert inches to centimeters."""
    return inch * 2.54


def cm_to_fraction(
    fig: matplotlib.figure.Figure, xy: tuple[float, float]
) -> tuple[float, float]:
    """Convert upper left cm to standard axes fraction.

    :param fig:
    :type fig: matplotlib.figures.Figure
    :param xy: (x, y) origin upper left
    :type xy: Tuple[float, float]
    :return: xfrac, yfrac, origin lower left
    :rtype: Tuple[float, float]
    """
    figsize = inch_to_cm(fig.get_size_inches())
    width = xy[0]
    height = figsize[1] - xy[1]
    return width / figsize[0], height / figsize[1]


def fraction_to_cm(
    fig: matplotlib.figure.Figure, xy: tuple[float, float]
) -> tuple[centimetres, centimetres]:
    """Convert standard axes fraction to upper left cm.

    :param fig:
    :type fig: matplotlib.figures.Figure
    :param xy: (x, y) axes fraction origin lower left
    :type xy: Tuple[float, float]
    :return: (x, y) cm origin upper left
    :rtype: Tuple[float, float]
    """
    figsize = inch_to_cm(fig.get_size_inches())
    return xy[0] * figsize[0], figsize[1] - (figsize[1] * xy[1])


# --- Classes ---
class CMTransform(Transform):
    """Convert coordinates from centimeters to figure fractions.

    Works on a Matplotlib figure, with the origin at the upper left.
    """

    input_dims = 2  # pyright: ignore[reportAssignmentType, reportIncompatibleMethodOverride]
    output_dims = 2  # pyright: ignore[reportAssignmentType, reportIncompatibleMethodOverride]
    has_inverse = True  # pyright: ignore[reportAssignmentType, reportIncompatibleMethodOverride]

    def __init__(self, fig: matplotlib.figure.Figure) -> None:
        """Initialize the CMTransform.

        :param fig: The figure to calculate the transform on.
        :type fig: matplotlib.figure.Figure
        """
        super().__init__()
        self.fig = fig

    def transform(self, values: ArrayLike) -> np.ndarray:
        """Transform cm coordinates (upper left origin) to figure fractions."""
        inch_coords = np.array(values) / 2.54
        figwidth, figheight = self.fig.get_size_inches()
        x, y = inch_coords.T
        return np.array([x / figwidth, 1 - (y / figheight)]).T  # flip y

    def inverted(self) -> InvertedCMTransform:
        """Return the inverse transform."""
        return InvertedCMTransform(self.fig)


class InvertedCMTransform(Transform):
    """Convert figure fractions to centimeters (upper left origin)."""

    input_dims = 2  # pyright: ignore[reportAssignmentType, reportIncompatibleMethodOverride]
    output_dims = 2  # pyright: ignore[reportAssignmentType, reportIncompatibleMethodOverride]
    has_inverse = True  # pyright: ignore[reportAssignmentType, reportIncompatibleMethodOverride]

    def __init__(
        self, fig: matplotlib.figure.Figure, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.fig = fig

    def transform(self, values: ArrayLike) -> np.ndarray:
        """Transform figure fractions to cm coordinates (upper left origin)."""
        # Convert figure coordinates to inches
        figwidth, figheight = self.fig.get_size_inches()
        x, y = np.array(values).T
        inch_coords = np.array(
            [x * figwidth, (1 - y) * figheight],
        ).T  # Flip y-axis back

        # Convert inches to cm
        return inch_coords * 2.54

    def inverted(self) -> CMTransform:
        """Return the inverse transform."""
        return CMTransform(self.fig)
