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
from ._utils import find_stack_level
from .grid import GuideGridClass
from .types import ExtentCM, centimetres

__all__ = ["FigureText", "LocationCM", "PanelAxes", "PanelLabel", "SciFigure"]

LocationCM = tuple[centimetres, centimetres, centimetres, centimetres]
"""Location in cm (x0, y0, x1, y1) or (x, y, w, h), origin upper left."""


class SciFigure(figure.Figure):
    """Figure that handles panel layout in cm with an upper left origin.

    A :class:`matplotlib.figure.Figure` with methods to set its size in cm
    (:meth:`set_size_cm`), add panels positioned in cm (:meth:`add_panel`), show a cm
    guide grid (:meth:`draw_grid`) and save with settings made for documents
    (:meth:`export`). Create one with :func:`scilayout.figure`.

    Attributes
    ----------
    grid : GuideGridClass
        Handler for the guide grid. Internal, use :meth:`draw_grid`.
    transCM : scilayout.locations.CMTransform
        Transform from cm (upper left origin) to figure fraction.

    Examples
    --------
    >>> import scilayout
    >>> fig = scilayout.figure()
    >>> fig.set_size_cm(12, 8)
    >>> ax = fig.add_panel((1.5, 1.5, 4.5, 2.5), method="bounds", panellabel="a")

    """

    grid: GuideGridClass

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialise a figure with extra scientific-figure ready features.

        Parameters
        ----------
        *args
            Positional arguments for :class:`matplotlib.figure.Figure`.
        **kwargs
            Keyword arguments for :class:`matplotlib.figure.Figure`. See
            https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html

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
        """Add a panel (axes) to the figure, positioned in cm.

        Parameters
        ----------
        location : tuple of float
            Location of the panel in cm from the upper left of the figure, read
            according to ``method``.
        panellabel : str, optional
            Letter to label the panel with, for example "a".
        method : {"bounds", "extent"}, optional
            How to interpret the location.
            "bounds" reads (x, y, width, height).
            "extent" reads (x0, y0, x1, y1), the upper left and lower right corners.
            Not specifying a method currently means "extent", but the default will
            change to "bounds" in a future release. Specify it to avoid the warning.
            The old names "bbox" and "size" are deprecated aliases of "extent" and
            "bounds".
        **kwargs
            Keyword arguments for :class:`PanelAxes`, which passes them to
            :class:`matplotlib.axes.Axes`.

        Returns
        -------
        PanelAxes
            The new panel.

        Raises
        ------
        ValueError
            If ``method`` is not recognised, ``location`` does not have four values, or
            the location is not valid for the method (for example a negative width).

        Examples
        --------
        >>> import scilayout
        >>> fig = scilayout.figure()
        >>> ax = fig.add_panel((1, 0.5, 5, 6), method="bounds")  # x, y, width, height
        >>> ax = fig.add_panel((1, 0.5, 6, 6.5), method="extent")  # x0, y0, x1, y1

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
        """Show the cm guide grid on the figure.

        The grid has markers every 1 cm (and half cm), with larger markers every 5 cm,
        measured from the upper left of the figure. It is removed by :meth:`clear`.

        Parameters
        ----------
        **kwargs
            Grid settings. Not implemented: giving any warns and they are ignored.

        Warns
        -----
        UserWarning
            If any keyword arguments are given.

        """
        # if kwargs are given warn that
        # changing settings with this function is not implemented
        if kwargs:
            # TODO: implement changing grid settings
            warnings.warn(
                "Setting grid settings with draw_grid() is not implemented.",
                stacklevel=find_stack_level(),
            )
        self.grid.show()

    def clear(self, keep_observers: bool = False) -> None:
        """Clear the figure, including the panels and the guide grid.

        Parameters
        ----------
        keep_observers : bool, optional
            Passed to :meth:`matplotlib.figure.Figure.clear`.

        """
        super().clear(keep_observers=keep_observers)
        if self.grid:
            self.grid._detach_ax()

    def clf(self, keep_observers: bool = False) -> None:
        """Clear the figure entirely. An alias of :meth:`clear` in matplotlib.

        Parameters
        ----------
        keep_observers : bool, optional
            Passed to :meth:`matplotlib.figure.Figure.clf`.

        """
        super().clf(keep_observers=keep_observers)

    def set_location(
        self,
        x: int,
        y: int,
        method: str = "px",
    ) -> None:
        """Set location of a figure window on the screen.

        Only the Qt backends are supported.

        Parameters
        ----------
        x : int
            Horizontal coordinate from the left of the screen.
        y : int
            Vertical coordinate from the top of the screen.
        method : {"px"}
            Units of ``x`` and ``y``. Only pixels are implemented.

        Raises
        ------
        NotImplementedError
            If ``method`` is not ``"px"`` or the backend is not Qt.
        RuntimeError
            If the figure has no window.

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
        """Export the figure to a file, with settings made for documents.

        The format comes from the file extension: ".png", ".svg", ".pdf" or ".eps".
        SVG text stays as text, PDF and EPS metadata that changes on every save is
        removed (so version control sees no change), and PNGs are transparent by
        default.

        Parameters
        ----------
        savepath : str or pathlib.Path
            The path to save the figure to.
        **kwargs
            Options for the export: ``dpi`` (300 by default), ``transparent_png``
            (True), ``bbox`` ("tight", or None to keep the full figure size) and
            ``allow_overwrite`` (True).

        Raises
        ------
        ValueError
            If the file extension is not recognised.
        FileExistsError
            If the file exists and ``allow_overwrite`` is False.

        """
        base.savefigure(self, savepath, **kwargs)

    def close(self) -> None:
        """Close the figure window (convenience for ``plt.close(fig)``)."""
        plt.close(self)


class PanelAxes(Axes):
    """Axes that are positioned in cm from the upper left of the figure.

    A :class:`matplotlib.axes.Axes` where the position is called a *location*, is in cm
    with the origin at the upper left of the figure, and is set and read with
    :meth:`set_location` and :meth:`get_location`. Create one with
    :meth:`SciFigure.add_panel`.

    Attributes
    ----------
    panellabel : PanelLabel or None
        The panel's label, or None if it has none. See :meth:`add_label`.

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
        """Create a panel on a figure.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            Figure to add the panel to.
        location : tuple of float
            Location of the panel in cm from the upper left of the figure, read
            according to ``method``.
        panellabel : str, optional
            Letter to label the panel with, for example "a".
        method : {"bounds", "extent"}, optional
            How to interpret ``location``. See :meth:`set_location`.
        **kwargs
            Keyword arguments for :class:`matplotlib.axes.Axes`.

        """
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
        """Set the location of the panel in cm.

        Parameters
        ----------
        location : tuple of float
            Coordinates from the upper left of the figure in cm, read according to
            ``method``.
        method : {"bounds", "extent"}, optional
            "bounds" reads (x, y, width, height).
            "extent" reads (x0, y0, x1, y1), the upper left and lower right corners.
            Not specifying a method currently means "extent", but the default will
            change to "bounds" in a future release. Specify it to avoid the warning.

        Raises
        ------
        ValueError
            If ``method`` is not recognised, ``location`` does not have four values, or
            the location is not valid for the method (for example a negative width).

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
        """Get the location of the panel in cm.

        Returns
        -------
        scilayout.types.Extent
            (x0, y0, x1, y1) in cm, origin at the upper left of the figure. It
            unpacks like a tuple and its fields are also available by name.

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
        """Add a label to the panel, or change its text if it already has one.

        Parameters
        ----------
        label : str
            Identifier string for the panel, for example "a".
        ha : str, optional
            Horizontal alignment. See :meth:`PanelLabel.set_alignment`.

        """
        # TODO: allow for more complexity at inisitalisation (especially x/y offsets, positions)
        if self.panellabel is not None:
            self.panellabel.text.set_text(label)
        else:
            self.panellabel = PanelLabel(self, label)
        if ha is not None:
            self.panellabel.set_alignment(h=ha)

    def clear(self) -> None:
        """Clear the axes, including the panel label."""
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

    The label's baseline starts at exactly the upper left corner of the axes and is then
    moved by the 'panellabel.xoffset' and 'panellabel.yoffset' style parameters (cm,
    negative is left and up). The defaults put the letter just above and to the left of
    the corner, clear of a 10 point y tick label at the top of the axis. Use a smaller
    (less negative) offset for smaller tick labels.

    The 'anchor position' is the top left corner of the associated PanelAxes.

    To change the properties of the text, use the ``text`` attribute directly,
    for example ``panellabel.text.set_horizontal_alignment("right")``.

    Attributes
    ----------
    ax : PanelAxes
        The panel the label belongs to.
    xoffset : float
        Horizontal offset from the panel's upper left corner, in cm.
    yoffset : float
        Vertical offset from the panel's upper left corner, in cm.
    text : matplotlib.text.Text
        The text object.

    """

    ax: PanelAxes
    xoffset: float
    yoffset: float
    text: Text

    def __init__(self, ax: PanelAxes, label: str) -> None:
        """Create the text that identifies the panel.

        Parameters
        ----------
        ax : PanelAxes
            The panel to label.
        label : str
            The label text. Changed to upper or lower case if the "panellabel.case"
            style parameter is set.

        """
        self.text = base.create_panel_label(ax, label)
        self.ax = ax
        self.xoffset = style.params["panellabel.xoffset"]
        self.yoffset = style.params["panellabel.yoffset"]
        self.set_offset(x=self.xoffset, y=self.yoffset)

    @property
    def anchorlocation(self) -> tuple:
        """The (x, y) location of the panel's upper left corner, in cm."""
        return self.ax.get_location()[0:2]

    def get_location(self) -> tuple[centimetres, centimetres]:
        """Get the position of the label on the figure.

        Returns
        -------
        tuple of float
            (x, y) in cm, origin at the upper left of the figure.

        """
        figfrac = self.text.get_position()
        return locations.fraction_to_cm(self.ax._fig, figfrac)

    def set_location(self, x: float | None = None, y: float | None = None) -> None:
        """Set the position of the label on the figure directly, in cm.

        Parameters
        ----------
        x : float, optional
            Horizontal position in cm from the left of the figure. Unchanged if None.
        y : float, optional
            Vertical position in cm from the top of the figure. Unchanged if None.

        """
        currentpos = self.get_location()
        tempxy = (currentpos[0] if x is None else x, currentpos[1] if y is None else y)
        convertedfrac = locations.cm_to_fraction(self.ax._fig, tempxy)
        setfrac = (convertedfrac[0], convertedfrac[1])
        self.text.set_position(setfrac)

    # TODO: add some method for determining position if it's on a plot graph (i.e. label over ylabel position?)

    def set_offset(self, x: float | None = None, y: float | None = None) -> None:
        """Set the position of the label relative to the panel's upper left corner.

        The offset is kept, so the label follows the panel when it is moved.

        Parameters
        ----------
        x : float, optional
            Distance (cm) to offset the label horizontally. Negative values move it
            left. Unchanged if None.
        y : float, optional
            Distance (cm) to offset the label vertically. Negative values move it up.
            Unchanged if None.

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

        Only ``h="right"`` currently has an effect: it moves the label 1 cm to the left
        of the panel. ``v`` is accepted but not used yet. For the alignment of the text
        itself use ``PanelLabel.text``, see
        https://matplotlib.org/stable/gallery/text_labels_and_annotations/text_alignment.html

        Parameters
        ----------
        h : str, optional
            Horizontal alignment, "left" by default.
        v : str, optional
            Vertical alignment. Not used yet.

        """
        # todo: change this behaviour?
        if h == "right":
            self.set_offset(x=-1)


class FigureText:
    """Text positioned on the figure in cm from its upper left corner.

    Attributes
    ----------
    text : matplotlib.text.Text
        The text object.

    """

    text: Text

    def __init__(
        self,
        x: centimetres,
        y: centimetres,
        text: str,
        figure: Figure,
        **kwargs: Any,
    ) -> None:
        """Create text on the figure.

        Parameters
        ----------
        x : float
            Horizontal position in cm from the left of the figure.
        y : float
            Vertical position in cm from the top of the figure.
        text : str
            The text to show.
        figure : matplotlib.figure.Figure
            The figure to add the text to.
        **kwargs
            Keyword arguments for :meth:`matplotlib.figure.Figure.text`.

        """
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
        """Set the position of the text in cm from the upper left of the figure.

        Parameters
        ----------
        x : float
            Horizontal position in cm from the left of the figure.
        y : float
            Vertical position in cm from the top of the figure.

        """
        x, y = locations.cm_to_fraction(cast("Figure", self.text.get_figure()), (x, y))
        self.text.set_position((x, y))

    def remove(self) -> None:
        """Remove the text from the figure (for use with live figures)."""
        self.text.remove()
        self.text.set_visible(False)
