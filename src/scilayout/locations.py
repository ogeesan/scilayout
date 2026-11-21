"""Convert between cm, inch, and fraction locations in matplotlib figures."""

from __future__ import annotations

import warnings
from typing import Any, Literal, overload

import matplotlib.figure
import numpy as np
from matplotlib.transforms import Affine2DBase

from ._utils import find_stack_level
from .types import Bound, Extent, ExtentCM, centimetres

__all__ = [
    "CMTransform",
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


def to_extent(location: tuple[float, ...], method: LocationMethod) -> ExtentCM:
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
class CMTransform(Affine2DBase):
    """Convert coordinates from centimeters to figure fractions.

    Works on a Matplotlib figure, with the origin at the upper left.
    The output is a figure fraction, so to place an artist with it, follow it with
    ``fig.transFigure``, which turns fractions into display coordinates.

    It is a matplotlib affine transform, so it combines with other transforms and
    follows the figure when it is resized.

    Examples
    --------
    >>> import scilayout
    >>> fig = scilayout.figure()
    >>> fig.set_size_cm(10, 5)
    >>> cm = scilayout.locations.CMTransform(fig)
    >>> cm.transform((0, 0))  # the upper left corner
    array([0., 1.])
    >>> text = fig.text(2, 1, "2 cm across, 1 cm down", transform=cm + fig.transFigure)

    """

    def __init__(self, fig: matplotlib.figure.Figure) -> None:
        """Initialize the CMTransform.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to calculate the transform on.

        """
        super().__init__()
        self.fig = fig
        # transFigure changes when the figure is resized: depend on it to know when
        # the matrix is out of date, including inside transforms combined with this one
        self.set_children(fig.transFigure)
        self._mtx: np.ndarray = np.identity(3)

    def get_matrix(self) -> np.ndarray:
        """Return the 3 x 3 matrix for the figure's current size."""
        if self._invalid:
            width, height = np.asarray(self.fig.get_size_inches()) * 2.54
            self._mtx = np.array(
                [[1 / width, 0, 0], [0, -1 / height, 1], [0, 0, 1]]
            )  # flip y
            self._invalid = 0
        return self._mtx

    def inverted(self) -> _InvertedCMTransform:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return the inverse transform."""
        return _InvertedCMTransform(self.fig)


class _InvertedCMTransform(Affine2DBase):
    """Convert figure fractions to centimeters (upper left origin).

    Get one with ``CMTransform(fig).inverted()``.
    """

    def __init__(self, fig: matplotlib.figure.Figure) -> None:
        """Initialize the inverse transform.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to calculate the transform on.

        """
        super().__init__()
        self.fig = fig
        self.set_children(fig.transFigure)
        self._mtx: np.ndarray = np.identity(3)

    def get_matrix(self) -> np.ndarray:
        """Return the 3 x 3 matrix for the figure's current size."""
        if self._invalid:
            width, height = np.asarray(self.fig.get_size_inches()) * 2.54
            self._mtx = np.array([[width, 0, 0], [0, -height, height], [0, 0, 1]])
            self._invalid = 0
        return self._mtx

    def inverted(self) -> CMTransform:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return the inverse transform."""
        return CMTransform(self.fig)


def __getattr__(name: str) -> Any:
    """Keep the old public name of the inverse transform working, with a warning."""
    if name == "InvertedCMTransform":
        warnings.warn(
            "InvertedCMTransform is deprecated and will be removed in scilayout "
            f"{REMOVAL_VERSION}, use CMTransform(fig).inverted() instead.",
            FutureWarning,
            stacklevel=find_stack_level(),
        )
        return _InvertedCMTransform
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
