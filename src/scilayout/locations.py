"""Convert between cm, inch, and fraction locations in matplotlib figures."""

from __future__ import annotations

import warnings
from typing import Any, Literal, overload

import matplotlib.figure
import numpy as np
from matplotlib.transforms import Transform
from numpy.typing import ArrayLike

from ._utils import find_stack_level
from .types import Bound, Extent, ExtentCM, centimetres

__all__ = [
    "CMTransform",
    "InvertedCMTransform",
    "LocationMethod",
    "cm_to_fraction",
    "cm_to_inch",
    "fraction_to_cm",
    "inch_to_cm",
    "locationcm_to_position",
]

LocationMethod = Literal["bounds", "extent"]
"""How to read a 4-tuple location.

- ``"bounds"``: (x, y, width, height)
- ``"extent"``: (x0, y0, x1, y1), the corners
"""

_DEPRECATED_METHODS: dict[str, LocationMethod] = {"size": "bounds", "bbox": "extent"}

REMOVAL_VERSION = "1.0"
"""The version in which the default ``method`` becomes ``"bounds"`` and the deprecated
method names are removed."""


def resolve_method(method: str | None) -> LocationMethod:
    """Validate a location ``method``, warning about deprecated usage.

    ``None`` (not specifying a method) currently means ``"extent"`` but this will
    change to ``"bounds"`` in version 1.0. The old names ``"bbox"`` and ``"size"`` are
    deprecated aliases of ``"extent"`` and ``"bounds"``, and will be removed in 1.0.

    Parameters
    ----------
    method : str | None
        ``"bounds"``, ``"extent"``, or a deprecated value.

    Returns
    -------
    LocationMethod
        ``"bounds"`` or ``"extent"``.

    Raises
    ------
    ValueError
        If ``method`` is not recognised.

    """
    if method is None:
        warnings.warn(
            "The default interpretation of a location tuple is changing from "
            "'extent' (x0, y0, x1, y1) to 'bounds' (x, y, width, height) in "
            f"scilayout {REMOVAL_VERSION}. Pass method='extent' to keep the current "
            "behaviour, or method='bounds' to adopt the new one.",
            FutureWarning,
            stacklevel=find_stack_level(),
        )
        return "extent"
    if method in _DEPRECATED_METHODS:
        new = _DEPRECATED_METHODS[method]
        warnings.warn(
            f"method={method!r} is deprecated and will be removed in scilayout "
            f"{REMOVAL_VERSION}, use method={new!r} instead.",
            FutureWarning,
            stacklevel=find_stack_level(),
        )
        return new
    if method in ("bounds", "extent"):
        return method  # pyright: ignore[reportReturnType]
    msg = f"method must be 'bounds' or 'extent', not {method!r}"
    raise ValueError(msg)


from .types import Models


def to_extent(location: tuple[float, ...] | Models, method: LocationMethod) -> ExtentCM:
    """Convert a 4-tuple location in cm to an extent (corners).

    A [`Bound`][scilayout.types.Bound] or [`Extent`][scilayout.types.Extent] instance
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

    Raises
    ------
    ValueError
        If ``location`` does not have four values, the extent is not ordered, or a
        width or height is negative.

    """
    if isinstance(location, Models):
        if isinstance(location, ExtentModel):
            return ExtentCM(location.x0, location.y0, location.x1, location.y1)
        else:
            return ExtentCM(
                location.x,
                location.y,
                location.x + location.width,
                location.y + location.height,
            )
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
    """Convert an upper left origin cm extent to a figure fraction rect.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to find the true size from.
    location_corners : tuple of float
        (x0, y0, x1, y1) corners in cm, origin at the upper left of the figure with y
        increasing downwards.

    Returns
    -------
    tuple of float
        (left, bottom, width, height) in figure fraction, origin at the lower left of
        the figure with y increasing upwards. This is the form matplotlib's
        ``add_axes`` and ``set_position`` take.

    Raises
    ------
    ValueError
        If ``x0 > x1`` or ``y0 > y1``.

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
    """Convert a position in cm from the upper left to figure fraction.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to find the size from.
    xy : tuple of float
        (x, y) in cm, origin at the upper left of the figure.

    Returns
    -------
    tuple of float
        (x, y) in figure fraction, origin at the lower left of the figure.

    """
    figsize = inch_to_cm(fig.get_size_inches())
    width = xy[0]
    height = figsize[1] - xy[1]
    return width / figsize[0], height / figsize[1]


def fraction_to_cm(
    fig: matplotlib.figure.Figure, xy: tuple[float, float]
) -> tuple[centimetres, centimetres]:
    """Convert a figure fraction position to cm from the upper left.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to find the size from.
    xy : tuple of float
        (x, y) in figure fraction, origin at the lower left of the figure.

    Returns
    -------
    tuple of float
        (x, y) in cm, origin at the upper left of the figure.

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

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to calculate the transform on.

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
