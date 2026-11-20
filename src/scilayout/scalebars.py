"""Movable scalebars for matplotlib plots."""

from typing import Any

import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.text import Text

from . import style
from .classes import PanelAxes


def _check_coord_system(coord_system: str) -> None:
    """Raise ValueError if the coordinate system is not recognised."""
    if coord_system not in ("fraction", "data", "cm"):
        msg = f"coordSystem must be 'fraction', 'data' or 'cm', not {coord_system!r}"
        raise ValueError(msg)


class ScaleBar:
    """Scale bar for matplotlib plots.

    Both horizontal and vertical scale bars.
    A scalebar that can be respositioned using the move() method.
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
    ) -> None:
        """Create a scalebar on a matplotlib axes.

        :param ax: Axes to draw the scalebar on
        :type ax: matplotlib.axes.Axes
        :param length: Length of the scalebar
        :type length: float or int
        :param xy: Position of the scalebar in data coordinates
        :type xy: tuple
        :param unit: Unit of the scalebar, optional
        :type unit: str
        :param orientation: Orientation of the scalebar. 'h' for horizontal (default), 'v' for vertical
        :type orientation: str, optional
        :param coordSystem: Units of the xy position. 'fraction' (default), 'data' or 'cm'
        :type coordSystem: str, optional
        :param hpos: Horizontal position of the text. Behaviour depends on orientation
        :type hpos: str
        :param vpos: Vertical position of the text. Behaviour depends on orientation
        :type vpos: str
        :param textstring: Text to display on the scalebar. Defaults to the length and unit
        :type textstring: str
        :param lw: Linewidth of the scalebar, default 1
        :type lw: float
        :param fontsize: Font size of the text, default 8
        :type fontsize: int
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
            if vpos not in ("top", "bottom"):
                msg = f"vpos must be 'top' or 'bottom', not {vpos!r}"
                raise ValueError(msg)
        else:
            if hpos is None:
                hpos = "left"
            if hpos not in ("left", "right"):
                msg = f"hpos must be 'left' or 'right', not {hpos!r}"
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
        self.lw = 1 if lw is None else lw
        self.fontsize = (
            style.params["scalebars.fontsize"] if fontsize is None else fontsize
        )

        self.text_pixel_pad_proportion = 0.5
        # self.test_line_pad_cm = 0.025  # TODO: express padding as cm

        self._initialise_scalebar(*xy)

    def _initialise_scalebar(self, x: float, y: float) -> None:
        """Initialise the scalebar and text objects."""
        if self.orientation == "h":
            if self.vpos == "top":
                va = "bottom"
            elif self.vpos == "bottom":
                va = "top"
            else:
                va = "center"
            text_kwargs: dict[str, Any] = {"ha": self.hpos, "va": va}
        else:
            if self.hpos == "left":
                ha = "right"
            elif self.hpos == "right":
                ha = "left"
            else:
                ha = "center"
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
        textstring = (
            f"{self.length} {self.unit}" if self.textstring is None else self.textstring
        )
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

        :param x: x-coordinate of the new position
        :type x: float
        :param y: y-coordinate of the new position
        :type y: float
        :param coordSystem: scale type of the new position. Defaults to object's unit type
        :type coordSystem: str, optional
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

        # Find line bbox
        self.line.get_window_extent(renderer)
        # TODO: make the line width change the padding

        # Convert text width to data coordinates
        inv_transform = self.ax.transData.inverted()
        if self.orientation == "h":
            text_xpos, text_ypos = np.mean(x_locs), y_locs[0]
            if self.vpos == "top":
                text_ypos = (
                    text_ypos + text_height_data * self.text_pixel_pad_proportion
                )
            elif self.vpos == "bottom":
                text_ypos = (
                    text_ypos - text_height_data * self.text_pixel_pad_proportion
                )
            elif self.vpos == "center":
                pass
            else:
                raise ValueError(f"Unknown vertical alignment: {self.vpos}")
        elif self.orientation == "v":
            text_xpos, text_ypos = x_locs[0], np.mean(y_locs)
            if self.hpos == "left":
                text_xpos = text_xpos - text_width_data * self.text_pixel_pad_proportion
            elif self.hpos == "right":
                text_xpos = text_xpos + text_width_data * self.text_pixel_pad_proportion
            else:
                raise ValueError(f"Unknown horizontal alignment: {self.hpos}")
        else:
            raise ValueError(f"Unknown orientation: {self.orientation}")

        self.text.set_position((float(text_xpos), float(text_ypos)))
        self.line.set_xdata(x_locs)
        self.line.set_ydata(y_locs)

        self.ax.figure.canvas.draw()  # to update the display of the modified objects

    def _find_x_y(
        self, x: float, y: float, coordSystem: str
    ) -> tuple[list[float], list[float]]:
        """Find the x and y coordinates of the scalebar.

        :param x: x-coordinate of the new position
        :type x: float
        :param y: y-coordinate of the new position
        :type y: float
        :param coordSystem: scale type of the new position ('fraction', 'data', 'cm')
        :type coordSystem: str
        :return: Coordinates of the scalebar in data coordinates
        :rtype: Tuple(List[float, float], List[float, float])
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
    ) -> None:
        """Create linked horizontal and vertical scale bars at the same position."""
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
        )
        self.ax = ax

    def move(self, x: float, y: float, coordSystem: str | None = None) -> None:
        """Move both scale bars to a new position."""
        self.x_scalebar.move(x, y, coordSystem)
        self.y_scalebar.move(x, y, coordSystem)
