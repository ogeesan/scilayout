"""
Convert between cm, inch, and fraction locations in matplotlib figures
"""

import numpy as np
import numpy as np
from matplotlib.transforms import Transform
    
def locationcm_to_position(fig, location_corners):
    """Convert an upper left origin cm extent to figure fraction rect

    :param fig: Figure window to find true size from
    :type fig: matplotlib.figures.Figure
    :param location_corners: (x1, y1, x2, y2), origin point is upper left of figure (y1 is visual up), cm units
    :type location_corners: Tuple[float, float, float, float]
    :return: (x1, y1, width, height), origin point is lower left of figure (y1 is visual down), fraction units
    :rtype: Tuple[float, float, float, float]
    """
    
    x0_cm, y0_cm, x1_cm, y1_cm = location_corners
    assert x1_cm >= x0_cm, "x1 must be greater than x0"
    assert y1_cm >= y0_cm, "y1 must be greater than y0"
    
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
    position = [left, bottom, width_figure, height_figure]
    return position


# todo: check precision conversions of integer
# setting to location .5 and back again gives a slight difference
def cm_to_inch(cm):
    return cm / 2.54


def inch_to_cm(inch):
    return inch * 2.54


def cm_to_fraction(fig, xy):
    """Convert upper left cm to standard axes fraction

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


def fraction_to_cm(fig, xy):
    """Convert standard axes fraction to upper left cm

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
    input_dims = 2
    output_dims = 2
    has_inverse = True

    def __init__(self, fig):
        super().__init__()
        self.fig = fig

    def transform(self, values):
        inch_coords = np.array(values) / 2.54
        figwidth, figheight = self.fig.get_size_inches()
        x, y = inch_coords.T
        return np.array([x / figwidth, 1 - (y / figheight)]).T  # flip y
    
    def inverted(self):
         return InvertedCMTransform(self.fig)
     

class InvertedCMTransform(Transform):
        input_dims = 2
        output_dims = 2
        has_inverse = True

        def __init__(self, fig, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fig = fig

        def transform(self, values):
            # Convert figure coordinates to inches
            figwidth, figheight = self.fig.get_size_inches()
            x, y = np.array(values).T
            inch_coords = np.array([x * figwidth, (1 - y) * figheight]).T  # Flip y-axis back
            
            # Convert inches to cm
            return inch_coords * 2.54

        def inverted(self):
            return CMTransform(self.fig)
