"""Classes for handling panel layout in cm with upper left origin."""

from __future__ import annotations

import contextlib
import warnings
from pathlib import Path
from typing import Any, cast

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import figure
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Text

from . import base, locations, style
from .grid import GuideGridClass
from .types import ExtentCM, centimetres

LocationCM = tuple[centimetres, centimetres, centimetres, centimetres]
"""Location in cm (x0, y0, x1, y1) or (x, y, w, h), origin upper left."""


# TODO: make docs here the best
class SciFigure(figure.Figure):
    """Figure object that handles panel layout in cm with upper left origin.

    Methods
    -------
    draw_grid()
        Add a centimetre grid overlay onto the figure.

    """

    grid: GuideGridClass
    """Handler for guide grid."""

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialise a figure with extra scientific-figure ready features.

        Arguments and keyword arguments are fed into matplotlib's figure.Figure.
        Please see https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html
        """
        # must initialise before super because it'll call clear
        self.grid = GuideGridClass(self)
        super().__init__(*args, **kwargs)
        self.transCM = locations.CMTransform(self)

    def set_size_cm(self, w: float, h: float) -> None:
        """Set size of figure in cm.

        Parameters
        ----------
        w : float
            Width (cm) of figure.
        h : float
            Height (cm) of figure.

        """
        base.set_figure_size_cm(self, w, h)
        # TODO: resize panels to preserve their position

    def add_panel(
        self,
        location: LocationCM,
        panellabel: str | None = None,
        method: str | None = None,
        **kwargs: Any,
    ) -> PanelAxes:
        """Add panel (axes) to the figure.

        Creates a PanelAxes object positioned with cms
        args and kwargs are passed to PanelAxes.
        Required args is location (x1, y1, x2, y2) in cm from top left corner of figure.

        Call signature ::

            fig.add_panel((1, .5, 5, 6.5), method="bounds")


        Parameters
        ----------
        location : tuple[float, float, float, float]
            Location of the panel in cm from the upper left of the figure.
            Read according to ``method``.
        panellabel : str | None
            Letter to initialise the panel with.
        method : {"bounds", "extent"}
            How to interpret the location.
            "bounds" reads (x, y, width, height).
            "extent" reads (x0, y0, x1, y1), the upper left and lower right corners.
            Not specifying a method currently means "extent", but the default will
            change to "bounds" in a future release. Specify it to avoid the warning.
            The old names "bbox" and "size" are deprecated aliases of "extent" and
            "bounds".
        kwargs : dict
            Key word arguments to pass to PanelAxes initialisation.

        Returns
        -------
        PanelAxes
            The panel object

        """
        # TODO: should this be return self.fig.add_axes(rect, axes_class=PanelAxes)
        # add_axes(rect, projection=None, polar=False, **kwargs)
        # add_axes(ax)
        # with rect being converted into bm?
        method = locations.resolve_method(method)
        return PanelAxes(
            self,
            location=location,
            panellabel=panellabel,
            method=method,
            **kwargs,
        )

    def draw_grid(
        self,
        **kwargs: Any,
    ) -> None:
        """Add cm grid guide to the figure."""
        if self.grid is None:
            self.grid = GuideGridClass(self, **kwargs)
        else:
            # if kwargs are given warn that
            # changing settings with this function is not implemented
            if kwargs:
                # TODO: implement changing grid settings
                warnings.warn(
                    "Setting grid settings with draw_grid() is not implemented.",
                    stacklevel=2,
                )
            self.grid.show()

    def clear(self, keep_observers: bool = False) -> None:
        """Clear the figure (including removal of grid)."""
        super().clear(keep_observers=keep_observers)
        if self.grid:
            self.grid._detach_ax()

    def clf(self, keep_observers: bool = False) -> None:
        """Clear the figure entirely."""
        super().clf(keep_observers=keep_observers)

    def set_location(
        self,
        x: int,
        y: int,
        method: str = "px",
    ) -> None:
        """Set location of a figure window on the screen.

        :param x: Horizontal coordinate from left
        :type x: int
        :param y: Vertical coordinate from top
        :type y: int
        :param method: Method to set location, defaults to "px"
        :type method: str, optional
        """
        # TODO: add support for other backends

        backend = mpl.get_backend()

        if method != "px":
            # TODO: add support for method='fraction' and 'cm'?
            msg = 'Only method="px" is implemented'
            raise NotImplementedError(msg)

        if not backend.startswith("Qt"):
            msg = f"Backend {backend} not implemented. Submit issue to add suport."
            raise NotImplementedError(msg)

        manager = self.canvas.manager
        if manager is None:
            msg = "Figure has no window manager"
            raise RuntimeError(msg)
        window = manager.window  # pyright: ignore[reportAttributeAccessIssue]
        _, _, dx, dy = window.geometry().getRect()
        window.setGeometry(x, y, dx, dy)

    def export(self, savepath: Path | str, **kwargs: Any) -> None:
        """Export the figure to a file.

        Parameters
        ----------
        savepath : str | Path
            The path to save the figure to
        kwargs : dict
            Additional arguments to pass to savefigure

        """
        base.savefigure(self, savepath, **kwargs)

    def close(self) -> None:
        """Close figure window (convenience function)."""
        plt.close(self)


class PanelAxes(Axes):
    """Extension of Axes object to handle panel layout in cm with upper left origin.

    To use cm 'location' is used instead of 'position' e.g. set_location().
    """

    panellabel: PanelLabel | None

    def __init__(
        self,
        fig: Figure,
        location: LocationCM,
        panellabel: str | None = None,
        method: str | None = None,
        **kwargs: Any,
    ) -> None:
        method = locations.resolve_method(method)
        rect = (0, 0, 1, 1)  # dummy rect
        super().__init__(fig, rect, **kwargs)
        fig.add_axes(self)  # apparently this isn't in the super or something
        # TODO: test this behaves as expected
        self.panellabel = None
        if panellabel is not None:
            self.add_label(panellabel)
        self.set_location(location, method=method)

    def set_location(
        self,
        location: LocationCM,
        method: str | None = None,
    ) -> None:
        """Set location of panel in cm.

        Parameters
        ----------
        location : tuple[float, float, float, float]
            Coordinates from the upper left of the figure in cm, read according to
            ``method``.
        method : {"bounds", "extent"}
            "bounds" reads (x, y, width, height).
            "extent" reads (x0, y0, x1, y1), the upper left and lower right corners.
            Not specifying a method currently means "extent", but the default will
            change to "bounds" in a future release. Specify it to avoid the warning.

        """
        extent = locations.to_extent(location, locations.resolve_method(method))
        self.set_position(locations.locationcm_to_position(self._fig, extent))
        if self.panellabel is not None:
            self.panellabel.set_offset(self.panellabel.xoffset, self.panellabel.yoffset)

    @property
    def _fig(self) -> Figure:
        """The parent figure."""
        return cast("Figure", self.get_figure())

    def get_location(self) -> ExtentCM:
        """Get location of axes in cm as an extent (x0, y0, x1, y1).

        The origin is the upper left corner of the figure.
        """
        # TODO: use self.get_figure().transCM?
        figsize = locations.inch_to_cm(self._fig.get_size_inches())
        bbox_pos = self.get_position().get_points()
        xmin, ymax = bbox_pos[0]
        xmax, ymin = bbox_pos[1]
        ymin = 1 - ymin
        ymax = 1 - ymax

        xmin = xmin * figsize[0]
        xmax = xmax * figsize[0]
        ymin = ymin * figsize[1]
        ymax = ymax * figsize[1]
        return ExtentCM(float(xmin), float(ymin), float(xmax), float(ymax))

    def add_label(
        self,
        label: str,
        ha: str | None = None,
    ) -> None:
        """Add a label to the panel, or set its value.

        Parameters
        ----------
        label : str
            Identifier string for the panel e.g. 'a'
        ha : str (optional)
            Horizontal alignment, defaults to None

        """
        # TODO: allow for more complexity at inisitalisation (especially x/y offsets, positions)
        if self.panellabel is not None:
            self.panellabel.text.set_text(label)
        else:
            self.panellabel = PanelLabel(self, label)
        if ha is not None:
            self.panellabel.set_alignment(h=ha)

    def clear(self) -> None:
        """Clear the axes."""
        # Handle the panel label during clear
        super().clear()
        # check if panellabel is attr
        if "panellabel" in self.__dict__ and self.panellabel is not None:
            # Newer versions of matplotlib do something funky here.
            with contextlib.suppress(NotImplementedError):
                self.panellabel.text.remove()
            self.panellabel = None


class PanelLabel:
    """A label for a multi-part figure.

    The letter has its initialisation position at exactly the upper left corner of the
    axes, so if you use `fill_yaxis` on it then the letter will be touching the data. An
    upper case 12 point letter is just under 0.5cm tall, so an offset of 0.1 looks good.

    The 'anchor position' is the top left corner of the associated PanelAxes.

    To change the properties of the text, use the `text` attribute directly.
    (e.g. `panellabel.text.set_horizontal_alignment('right')`)

    """

    ax: PanelAxes
    xoffset: float
    """cm from top left corner"""
    yoffset: float
    """cm from top left corner"""
    text: Text
    """The actual text object"""

    def __init__(self, ax: PanelAxes, label: str) -> None:
        """Create text item to identify the panel."""
        self.text = base.create_panel_label(ax, label)
        self.ax = ax
        self.xoffset = style.params["panellabel.xoffset"]
        self.yoffset = style.params["panellabel.yoffset"]
        self.set_offset(x=self.xoffset, y=self.yoffset)

    @property
    def anchorlocation(self) -> tuple:
        """Top left location of the panel."""
        return self.ax.get_location()[0:2]

    def get_location(self) -> tuple[centimetres, centimetres]:
        """Get position on figure in cm."""
        figfrac = self.text.get_position()
        return locations.fraction_to_cm(self.ax._fig, figfrac)

    def set_location(self, x: float | None = None, y: float | None = None) -> None:
        """Set position of label on figure in cm directly."""
        currentpos = self.get_location()
        tempxy = (currentpos[0] if x is None else x, currentpos[1] if y is None else y)
        convertedfrac = locations.cm_to_fraction(self.ax._fig, tempxy)
        setfrac = (convertedfrac[0], convertedfrac[1])
        self.text.set_position(setfrac)

    # TODO: add some method for determining position if it's on a plot graph (i.e. label over ylabel position?)

    def set_offset(self, x: float | None = None, y: float | None = None) -> None:
        """Set position of label relative to the upper left corner of the axes.

        Parameters
        ----------
        x : float
            Distance (cm) from location to horizontally offset label.
            Negative values move label left.
        y : float
            Distance (cm) from location to vertically offset label.
            Negative values move label upwards.

        """
        # x_cm, y_cm = fraction_to_cm(self.ax.get_figure(), self.text.get_location())
        true_x, true_y = self.anchorlocation[0], self.anchorlocation[1]
        x = self.xoffset if x is None else x
        y = self.yoffset if y is None else y
        x_cm = true_x + x
        y_cm = true_y + y
        self.xoffset = x
        self.yoffset = y
        self.set_location(x_cm, y_cm)

    def set_alignment(self, h: str = "left", v: str = "baseline") -> None:
        """Align the panel letter.

        For more info on alignment options see:
        https://matplotlib.org/stable/gallery/text_labels_and_annotations/text_alignment.html

        Parameters
        ----------
        h : str
            Text horizontal alignment
        v : str
            Text vertical alignment

        """
        # todo: change this behaviour?
        if h == "right":
            self.set_offset(x=-1)


class FigureText:
    """A text object that is positioned relative to the figure."""

    text: Text
    """Text object."""

    def __init__(
        self,
        x: centimetres,
        y: centimetres,
        text: str,
        figure: Figure,
        **kwargs: Any,
    ) -> None:
        """Create FigureText object."""
        x, y = locations.cm_to_fraction(figure, (x, y))
        self.text = figure.text(
            x,
            y,
            text,
            figure=figure,
            transform=figure.transFigure,
            **kwargs,
        )

    def set_position(self, x: centimetres, y: centimetres) -> None:
        """Set position of figure text in cm."""
        x, y = locations.cm_to_fraction(cast("Figure", self.text.get_figure()), (x, y))
        self.text.set_position((x, y))

    def remove(self) -> None:
        """Remove the text from the figure (for use with live figures)."""
        self.text.remove()
        self.text.set_visible(False)
