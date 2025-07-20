__version__ = "0.0.1b8"
__all__ = ["__version__"]
# Import dependencies
import matplotlib.pyplot as plt

# Import sub-modules
from . import (
    classes,
    locations,
    scalebars,
    stats,
    style,
)

def figure(**kwargs):
    """Wrapper for plt.figure() that returns a SciFigure object

    :return: SciFigure object (the plot window)
    :rtype: scilayout.figures.SciFigure
    """
    if 'FigureClass' in kwargs:
        raise ValueError("Cannot set FigureClass in scilayout.figure(), use scilayout.classes.SciFigure instead.")
    return plt.figure(FigureClass=classes.SciFigure, **kwargs)
