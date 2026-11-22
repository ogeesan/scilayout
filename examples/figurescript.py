"""Demonstration of using scilayout to create a figure iPython and code sections.

This file is intended to be run using sections in an iPython notebook.
The sections are separated by '# %%' and can be run individually.
The code in each section is intended to be run in sequence.
Code sections are supported by PyCharm and VS Code.
"""

# %% Imports
import scilayout

# The matplotlib magic displays plots in a figure window
#!%matplotlib

# %% Create some dummy data from matplotlib and numpy
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

# %%
# Create a figure
fig = scilayout.figure(num="SciLayout Example")

# fig.clear() is called often so figures are not cluttered with old plots
# Keeping fig creation in its own section allows for easy re-running of the figure creation following fig.clear()

# %% Generate the panels
# Here we generate three plots on the same figure.
# The spacing of the plots and the order of generation do not matter as we can modify them later.
# In reality, the plots would be generated in a function.
# If these functions are in another file, then importlib.reload can be used to modify the functions and re-run the figure creation conveniently.

fig.clear()
fig.draw_grid()
ax_lineplot = fig.add_panel((1, 1, 5, 5))
ax_lineplot.plot(x, y)

ax_scatter = fig.add_panel((1, 6, 5, 11), method="bbox")
ax_scatter.scatter(x, y, color="r", s=5)

ax_hist = fig.add_panel((6, 1, 5, 5), method="size")
ax_hist.hist(y, bins=20)

# %% Reconfigure the layout

x1 = 1.5
x2, y2 = 5, 2.5

ax_scatter.add_label("a")
ax_scatter.set_location((x1, 0.5, x2, y2), method="size")
ax_scatter.set_xlabel("x value")
ax_scatter.set_ylabel("y value")

ax_lineplot.set_location((x1, 6, x2, y2), method="size")
ax_lineplot.add_label("b")
ax_lineplot.set_xlabel("x value")
ax_lineplot.set_ylabel("y value")

ax_hist.set_location((8.5, 0.5, 3, 6.5), method="size")
ax_hist.add_label("c")
ax_hist.panellabel.set_offset(x=-1.55)
ax_hist.set_xlabel("y value")
ax_hist.set_ylabel("Count")

# %%
# Note how panel b is slightly out of position.
# We can adjust the position of just this panel:
ax_lineplot.set_location((x1, 4.5, x2, y2), method="size")

# This workflow allows for easy adjustment of the layout without needing to regenerate the plots.
# It could be run in the console for small changes.
# Entirely new layouts could be generated in a new section.
# %%
