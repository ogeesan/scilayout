"""Movable scalebars for matplotlib plots."""

import warnings
from typing import Any

import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.text import Text

from . import style
from ._utils import find_stack_level
from .classes import PanelAxes

__all__ = ["LinkedScaleBar", "ScaleBar"]

CM_PER_INCH = 2.54
CM_PER_POINT = CM_PER_INCH / 72


def _check_coord_system(coord_system: str) -> None:
    """Raise ValueError if the coordinate system is not recognised."""
    if coord_system not in ("fraction", "data", "cm"):
        msg = f"coordSystem must be 'fraction', 'data' or 'cm', not {coord_system!r}"
        raise ValueError(msg)


def _open_gap(
    x_locs: list[float], y_locs: list[float], gap: float
) -> tuple[list[float], list[float]]:
    """Split a line in two, leaving ``gap`` (data units) empty around its middle.

    The two halves are joined by a NaN so they stay a single matplotlib line. If the
    gap is at least as long as the line, nothing is drawn: zero-length pieces would
    still show as dots because of the line's projecting caps.
    """
    (x0, x1), (y0, y1) = x_locs, y_locs
    length = float(np.hypot(x1 - x0, y1 - y0))
    if length == 0:
        return x_locs, y_locs
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    nan = float("nan")
    if gap >= length:
        return [nan, nan], [nan, nan]
    half = gap / 2
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return (
        [x0, mx - ux * half, nan, mx + ux * half, x1],
        [y0, my - uy * half, nan, my + uy * half, y1],
    )


class ScaleBar:
    """Scale bar for matplotlib plots.

    Horizontal or vertical, with text that can sit beside the bar or in a break in it.
    A scalebar can be repositioned using the [`move`][scilayout.scalebars.ScaleBar.move] method.

    Attributes
    ----------
    line : matplotlib.lines.Line2D
        The bar.
    text : matplotlib.text.Text
        The label.
    pad : float
        Gap in cm between the edge of the line and the text.

    """

    line: Line2D
    text: Text

    def __init__(
        self,
        ax: Axes,
        xy: tuple[float, float],
        length: float,
        unit: str | None = None,
        coordSystem: str = "fraction",
        orientation: str = "h",
        hpos: str | None = None,
        vpos: str | None = None,
        transform: str = "transData",
        textstring: str | None = None,
        lw: float | None = None,
        fontsize: float | None = None,
        pad: float | None = None,
    ) -> None:
        """Create a scalebar on a matplotlib axes.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axes to draw the scalebar on.
        xy : tuple of float
            Position of the start of the scalebar (its left end if horizontal, its
            lower end if vertical), in units of ``coordSystem``.
        length : float
            Length of the scalebar in data units.
        unit : str, optional
            Unit of the scalebar, shown after the length in the default text.
        coordSystem : {"fraction", "data", "cm"}, optional
            Units of ``xy``: "fraction" of the axes (default), "data" coordinates, or
            "cm" from the upper left of the figure (needs a ``PanelAxes``).
        orientation : {"h", "horizontal", "v", "vertical"}, optional
            Orientation of the scalebar, horizontal by default.
        hpos : {"left", "center", "right"}, optional
            Where the text sits horizontally. Only used for a vertical bar, where it is
            "left" by default. "center" puts the text in the middle of the bar, with a
            gap in the bar around the text.
        vpos : {"top", "center", "bottom"}, optional
            Where the text sits vertically. Only used for a horizontal bar, where it is
            "bottom" by default. "center" puts the text in the middle of the bar, with
            a gap in the bar around the text.
        transform : {"transData", "transAxes"}, optional
            Transform of the scalebar. Only "transData" is implemented.
        textstring : str, optional
            Text to display. Defaults to the length and unit.
        lw : float, optional
            Linewidth of the scalebar. Defaults to the "scalebars.linewidth" style
            parameter.
        fontsize : float, optional
            Font size of the text. Defaults to the "scalebars.fontsize" style parameter.
        pad : float, optional
            Gap in cm between the edge of the line and the text. It applies beside the
            bar and, for text centred on the bar, on each side of the text in the break
            in the bar. Defaults to the "scalebars.pad" style parameter. It can be
            changed later, followed by [`move`][scilayout.scalebars.ScaleBar.move].

        Raises
        ------
        ValueError
            If ``orientation``, ``hpos``, ``vpos``, ``coordSystem`` or ``transform`` is
            not one of the allowed values, or ``pad`` is negative.
        NotImplementedError
            If ``transform`` is "transAxes".
        TypeError
            If ``coordSystem`` is "cm" and ``ax`` is not a ``PanelAxes``.

        Warns
        -----
        UserWarning
            If the text is centred on the bar but is longer than the bar, in which
            case the bar is not drawn.

        """
        # Sort out orientations
        if orientation in ("horizontal", "h"):
            orientation = "h"
        elif orientation in ("vertical", "v"):
            orientation = "v"
        else:
            msg = f"orientation must be 'h' or 'v', not {orientation!r}"
            raise ValueError(msg)
        if orientation == "h":
            if vpos is None:
                vpos = "bottom"
            if vpos not in ("top", "center", "bottom"):
                msg = f"vpos must be 'top', 'center' or 'bottom', not {vpos!r}"
                raise ValueError(msg)
        else:
            if hpos is None:
                hpos = "left"
            if hpos not in ("left", "center", "right"):
                msg = f"hpos must be 'left', 'center' or 'right', not {hpos!r}"
                raise ValueError(msg)
        vpos = vpos if vpos is not None else "center"
        hpos = hpos if hpos is not None else "center"

        _check_coord_system(coordSystem)
        if transform not in ("transAxes", "transData"):
            msg = f"transform must be 'transAxes' or 'transData', not {transform!r}"
            raise ValueError(msg)
        if transform == "transAxes":
            msg = "transAxes not yet implemented"
            raise NotImplementedError(msg)

        self.ax = ax
        self.xypos = xy
        self.coordSystem = coordSystem
        self._transform = transform  # for now this cannot be changed after creation
        self.orientation = orientation
        self.length = length

        # Text items
        self.unit = unit
        self.textstring = textstring
        self.hpos = hpos
        self.vpos = vpos
        self.lw = style.params["scalebars.linewidth"] if lw is None else lw
        self.fontsize = (
            style.params["scalebars.fontsize"] if fontsize is None else fontsize
        )

        pad = style.params["scalebars.pad"] if pad is None else pad
        if pad < 0:
            msg = f"pad must not be negative, got {pad}"
            raise ValueError(msg)
        self.pad = pad

        self._initialise_scalebar(*xy)

    def _initialise_scalebar(self, x: float, y: float) -> None:
        """Initialise the scalebar and text objects."""
        if self.orientation == "h":
            # text sits on the opposite side of its anchor to the bar
            va = {"top": "bottom", "bottom": "top", "center": "center"}[self.vpos]
            text_kwargs: dict[str, Any] = {"ha": self.hpos, "va": va}
        else:
            ha = {"left": "right", "right": "left", "center": "center"}[self.hpos]
            text_kwargs = {"rotation": 90, "ha": ha, "va": self.vpos}

        text_xpos, text_ypos = 0, 0
        x_locs, y_locs = [0, 1], [0, 1]
        transform = (
            self.ax.transAxes if self._transform == "transAxes" else self.ax.transData
        )
        self.line = self.ax.plot(
            x_locs,
            y_locs,
            "k",
            lw=self.lw,
            transform=transform,
            clip_on=False,
        )[0]
        if self.textstring is not None:
            textstring = self.textstring
        elif self.unit is None:
            textstring = f"{self.length}"
        else:
            textstring = f"{self.length} {self.unit}"
        self.text = self.ax.text(
            text_xpos,
            text_ypos,
            textstring,
            transform=transform,
            size=self.fontsize,
            **text_kwargs,
        )
        self.move(x, y)

    def move(self, x: float, y: float, coordSystem: str | None = None) -> None:
        """Move the scalebar to a new position.

        Parameters
        ----------
        x : float
            x-coordinate of the new position.
        y : float
            y-coordinate of the new position.
        coordSystem : {"fraction", "data", "cm"}, optional
            Units of ``x`` and ``y``. Defaults to the units the scalebar was created
            with.

        Raises
        ------
        ValueError
            If ``coordSystem`` is not recognised.

        """
        coordSystem = self.coordSystem if coordSystem is None else coordSystem
        _check_coord_system(coordSystem)

        self._update_appearance()

        x_locs, y_locs = self._find_x_y(x, y, coordSystem)

        # Calculate text width in display coordinates
        renderer = self.ax.get_figure().canvas.get_renderer()  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]
        text_bbox = self.text.get_window_extent(renderer)
        inv_transform = self.ax.transData.inverted()
        text_width_data = (
            inv_transform.transform((text_bbox.width, 0))[0]
            - inv_transform.transform((0, 0))[0]
        )
        text_height_data = (
            inv_transform.transform((0, text_bbox.height))[1]
            - inv_transform.transform((0, 0))[1]
        )

        # The text starts `pad` cm from the edge of the line, which is half the line
        # width (in points) beyond the line's centre. Convert to data coordinates, where
        # an inverted axis gives a negative distance that moves the text the right way.
        dpi = self.ax.get_figure().dpi  # pyright: ignore[reportOptionalMemberAccess]
        from_centre_px = (self.pad + self.lw * CM_PER_POINT / 2) / CM_PER_INCH * dpi
        pad_x_data = (
            inv_transform.transform((from_centre_px, 0))[0]
            - inv_transform.transform((0, 0))[0]
        )
        pad_y_data = (
            inv_transform.transform((0, from_centre_px))[1]
            - inv_transform.transform((0, 0))[1]
        )

        gap = 0.0  # length of bar left empty around text centred on the bar
        if self.orientation == "h":
            text_xpos, text_ypos = np.mean(x_locs), y_locs[0]
            if self.vpos == "center":
                gap = abs(text_width_data) + 2 * abs(pad_x_data)
            else:
                text_ypos = (
                    text_ypos + pad_y_data
                    if self.vpos == "top"
                    else text_ypos - pad_y_data
                )
        else:
            text_xpos, text_ypos = x_locs[0], np.mean(y_locs)
            if self.hpos == "center":
                gap = abs(text_height_data) + 2 * abs(pad_y_data)
            else:
                text_xpos = (
                    text_xpos + pad_x_data
                    if self.hpos == "right"
                    else text_xpos - pad_x_data
                )

        if gap > 0:
            bar_length = float(np.hypot(x_locs[1] - x_locs[0], y_locs[1] - y_locs[0]))
            if 0 < bar_length <= gap:
                warnings.warn(
                    f"The text {self.text.get_text()!r} needs {gap:.3g} data units "
                    f"but the scale bar is only {bar_length:.3g} long, so the bar is "
                    "hidden. Shorten the text, lengthen the bar or move the text off "
                    "the bar.",
                    stacklevel=find_stack_level(),
                )
            x_locs, y_locs = _open_gap(x_locs, y_locs, gap)

        self.text.set_position((float(text_xpos), float(text_ypos)))
        self.line.set_xdata(x_locs)
        self.line.set_ydata(y_locs)

        self.ax.figure.canvas.draw()  # to update the display of the modified objects

    def _find_x_y(
        self, x: float, y: float, coordSystem: str
    ) -> tuple[list[float], list[float]]:
        """Find the x and y coordinates of the scalebar.

        Parameters
        ----------
        x : float
            x-coordinate of the new position.
        y : float
            y-coordinate of the new position.
        coordSystem : {"fraction", "data", "cm"}
            Units of ``x`` and ``y``.

        Returns
        -------
        x_locs : list of float
            x data coordinates of the two ends of the bar.
        y_locs : list of float
            y data coordinates of the two ends of the bar.

        """
        if coordSystem == "fraction":
            x, y = self.ax.transAxes.transform((x, y))
            x, y = self.ax.transData.inverted().transform((x, y))
        elif coordSystem == "cm":
            if not isinstance(self.ax, PanelAxes):
                msg = "coordSystem 'cm' requires the scalebar axes to be a PanelAxes"
                raise TypeError(msg)
            x0, y0, x1, y1 = (
                self.ax.get_location()
            )  # position in cm from top left of figure
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            xscale = (x1 - x0) / (xlim[1] - xlim[0])
            yscale = (y1 - y0) / (ylim[1] - ylim[0])
            x = xlim[0] + (x - x0) / xscale
            y = ylim[1] - (y - y0) / yscale  # y is inverted
        elif coordSystem == "data":
            pass
        else:
            raise ValueError(f"Unknown coordinate system: {coordSystem}")

        if self.orientation == "h":
            x_locs = [x, x + self.length]
            y_locs = [y, y]
        else:
            x_locs = [x, x]
            y_locs = [y, y + self.length]
        return x_locs, y_locs

    def _update_appearance(self) -> None:
        """Update the appearance of the scalebar."""
        self.text.set_fontsize(self.fontsize)
        self.line.set_linewidth(self.lw)
        self.ax.figure.canvas.draw()


class LinkedScaleBar:
    """A horizontal and a vertical scale bar that are moved together."""

    def __init__(
        self,
        ax: Axes,
        xy: tuple[float, float],
        x_length: float,
        y_length: float,
        x_unit: str | None = None,
        y_unit: str | None = None,
        coordSystem: str = "fraction",
        hat: str | None = None,
        vat: str | None = None,
        transform: str = "transData",
        x_textstring: str | None = None,
        y_textstring: str | None = None,
        lw: float | None = None,
        pad: float | None = None,
    ) -> None:
        """Create linked horizontal and vertical scale bars at the same position.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axes to draw the scalebars on.
        xy : tuple of float
            Position of the shared corner, in units of ``coordSystem``.
        x_length : float
            Length of the horizontal bar in data units.
        y_length : float
            Length of the vertical bar in data units.
        x_unit : str, optional
            Unit of the horizontal bar.
        y_unit : str, optional
            Unit of the vertical bar.
        coordSystem : {"fraction", "data", "cm"}, optional
            Units of ``xy``.
        hat : {"left", "center", "right"}, optional
            Horizontal position of the vertical bar's text.
        vat : {"top", "center", "bottom"}, optional
            Vertical position of the horizontal bar's text.
        transform : {"transData", "transAxes"}, optional
            Transform of the scalebars. Only "transData" is implemented.
        x_textstring : str, optional
            Text of the horizontal bar. Defaults to its length and unit.
        y_textstring : str, optional
            Text of the vertical bar. Defaults to its length and unit.
        lw : float, optional
            Linewidth of both bars.
        pad : float, optional
            Gap in cm between the edge of each line and its text.
            Defaults to the "scalebars.pad" style parameter.

        """
        if vat is None:
            vat = "bottom"
        self.x_scalebar = ScaleBar(
            ax,
            xy,
            x_length,
            x_unit,
            coordSystem,
            orientation="h",
            vpos=vat,
            transform=transform,
            textstring=x_textstring,
            lw=lw,
            pad=pad,
        )
        self.y_scalebar = ScaleBar(
            ax,
            xy,
            y_length,
            y_unit,
            coordSystem,
            orientation="v",
            hpos=hat,
            transform=transform,
            textstring=y_textstring,
            lw=lw,
            pad=pad,
        )
        self.ax = ax

    def move(self, x: float, y: float, coordSystem: str | None = None) -> None:
        """Move both scale bars to a new position.

        Parameters
        ----------
        x : float
            x-coordinate of the shared corner.
        y : float
            y-coordinate of the shared corner.
        coordSystem : {"fraction", "data", "cm"}, optional
            Units of ``x`` and ``y``. Defaults to the units the bars were created with.

        """
        self.x_scalebar.move(x, y, coordSystem)
        self.y_scalebar.move(x, y, coordSystem)
