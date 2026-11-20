"""scilayout package.

This package provides tools for creating and managing scientific figures with a focus on
layout in centimeters and an upper-left origin. It includes classes for figures, axes,
text, and scalebars.

Public API
----------
``scilayout.figure()`` creates a figure. The main classes are available directly from
the package (``SciFigure``, ``PanelAxes``, ``PanelLabel``, ``FigureText``,
``ScaleBar``, ``LinkedScaleBar`` and ``StatsLine``) and in these modules:

- ``classes``: figure, panel, panel label and figure text
- ``scalebars``: ``ScaleBar`` and ``LinkedScaleBar``
- ``stats``: ``StatsLine``
- ``style``: the style parameters (``params``, ``use``, ``reset``)
- ``locations``: conversions between cm, inches and figure fraction
- ``types``: ``Extent`` and ``Bound`` and their unit aliases

``base`` and ``grid`` are internal. They stay importable but may change without notice.
Use ``SciFigure.export`` to save a figure and ``SciFigure.draw_grid`` for the guide grid.
"""

from typing import Any, cast

import matplotlib.pyplot as plt

from . import (
    base,  # internal
    classes,
    grid,  # internal
    locations,
    scalebars,
    stats,
    style,
    types,
)
from .classes import FigureText, PanelAxes, PanelLabel, SciFigure
from .scalebars import LinkedScaleBar, ScaleBar
from .stats import StatsLine

__version__ = "0.1.2"
__all__ = [
    "FigureText",
    "LinkedScaleBar",
    "PanelAxes",
    "PanelLabel",
    "ScaleBar",
    "SciFigure",
    "StatsLine",
    "__version__",
    "classes",
    "figure",
    "locations",
    "scalebars",
    "stats",
    "style",
    "types",
]


def figure(**kwargs: Any) -> classes.SciFigure:
    """Create a SciFigure object.

    This function wraps ``plt.figure()``. See
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
    for the figure arguments.

    Parameters
    ----------
    **kwargs
        Keyword arguments for :func:`matplotlib.pyplot.figure`, for example
        ``figsize`` or ``num``. ``FigureClass`` cannot be set.

    Returns
    -------
    SciFigure
        The new figure (the plot window).

    Raises
    ------
    ValueError
        If ``FigureClass`` is given.

    Examples
    --------
    >>> import scilayout
    >>> fig = scilayout.figure()
    >>> ax_1 = fig.add_panel((1, 2, 4, 5), method="bounds")

    """
    if "FigureClass" in kwargs:
        msg = "Cannot set FigureClass in scilayout.figure(), use scilayout.classes.SciFigure instead."
        raise ValueError(msg)
    return cast(classes.SciFigure, plt.figure(FigureClass=classes.SciFigure, **kwargs))
