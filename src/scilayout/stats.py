"""Helper functions and classes for plotting stats information on an axes."""

from matplotlib import transforms
from matplotlib.axes import Axes
from matplotlib.transforms import Transform

__all__ = ["StatsLine"]


class StatsLine:
    """A horizontal statistical line with vertical drops at each end."""

    def __init__(self, ax: Axes, y: float, x0: float, x1: float) -> None:
        """Draw a horizontal statistical line with a drop at each end.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axes to draw the line on.
        y : float
            y location of the line as a fraction of the axes height.
        x0 : float
            x location of the start of the line in data coordinates.
        x1 : float
            x location of the end of the line in data coordinates.

        """
        self.ax = ax
        self.y = y
        self.x0 = x0
        self.x1 = x1
        self.main_bar = None
        self.right_drop = None
        self.left_drop = None
        self.linewidth = 1
        self.color = "black"
        self.drop_amount = 0.025
        self.transform = transforms.blended_transform_factory(
            ax.transData, ax.transAxes
        )
        self.draw()

    def draw(self) -> None:
        """Draw/redraw the line on the axis."""
        # remove existing lines
        for line in [self.main_bar, self.left_drop, self.right_drop]:
            if line is not None:
                line[0].remove()

        # Save current axis limits (.plot() may alter them)
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # TODO: implement style support here
        # turn off clip
        stylekwargs = {
            "color": self.color,
            "linewidth": self.linewidth,
            "transform": self.transform,
            "clip_on": False,
            "label": "_nolegend_",
        }

        self.main_bar = self.ax.plot(
            [self.x0, self.x1], [self.y, self.y], **stylekwargs
        )
        self.left_drop = self.ax.plot(
            [self.x0, self.x0], [self.y, self.y - self.drop_amount], **stylekwargs
        )
        self.right_drop = self.ax.plot(
            [self.x1, self.x1], [self.y, self.y - self.drop_amount], **stylekwargs
        )

        # Restore the xy limits
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

    def set_transform(self, x: str = "data", y: str = "axes") -> None:
        """Set the transform for the stat bar.

        Parameters
        ----------
        x : {"data", "axes"}
            Coordinates ``x0`` and ``x1`` are given in. "data" is the data coordinates
            of the axis, "axes" is the proportion of the axis width.
        y : {"data", "axes"}
            Coordinates ``y`` is given in. "axes" is the proportion of the axis height,
            so resizing the axis does not change where the line sits relative to it.

        Raises
        ------
        ValueError
            If ``x`` or ``y`` is not "data" or "axes".

        """
        transform: dict[str, Transform] = {}
        for key, val in zip(["x", "y"], [x, y], strict=True):
            if val == "data":
                transform[key] = self.ax.transData
            elif val == "axes":
                transform[key] = self.ax.transAxes
            else:
                raise ValueError(f"Unknown transform type {val}")
        self.transform = transforms.blended_transform_factory(
            transform["x"], transform["y"]
        )
        self.draw()
