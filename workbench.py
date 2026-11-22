# %%
from importlib import reload

import matplotlib.pyplot as plt
import numpy as np

import scilayout

# %%
fig = scilayout.figure()
fig.canvas.manager.window.setGeometry(-1030, 381, 802, 644) # if the laptop screen is active

# %%
fig.clear()
ax = fig.add_panel((1, 1, 6, 6))
# %%
from scilayout import scalebars
reload(scalebars)
ax.clear()

# ax.set_xlim((0, 5))
yscalebar = scalebars.ScaleBar(ax, (0.5, 0.5), .3, unit='data', orientation='v', hpos='left')
xscalebar = scalebars.ScaleBar(ax, (.4, .4), .2, unit='data', orientation='h', vpos='bottom')
scalebar = scalebars.LinkedScaleBar(ax, (0.7, 0.5), .3, .7, x_unit='data', y_unit='testy', lw=2)
# %%
scalebar.move(10, 10, 'cm')
# %%
ax.clear()
class MiniScaleBar(ScaleBar):
    def __init__(self, ax, xy, length, coordSystem, transform):
        super().__init__(ax, length, xy, unit='data', orientation='h', coordSystem=coordSystem, transform=transform)
    

arg_length = 1
arg_coordSystem = 'fraction'
arg_transform = 'transAxes'
scalebar = MiniScaleBar(ax, (.2, .5), arg_length, arg_coordSystem, arg_transform)


x, y, coordSystem = (.2, .5, 'fraction')
x, y, coordSystem = (3, 5.5, 'cm')
x, y, coordSystem = (3, 5.5, 'data')
self = scalebar
# develop the _find_x_y method
# Handle transAxes and transData

if self._transform == 'transAxes':
    if coordSystem == 'fraction':
        x_locs = [x, x + length]
        y_locs = [y, y]

# %%
ax.clear()
ax.set_xlim((0, 10))
ax.set_ylim((0, 10))

x, y = 1, 3

test = ax.annotate('', xy=(0, 0), xytext=(.5, .5), xycoords='data', textcoords='data', arrowprops=dict(arrowstyle='-', lw=1))

# %%

# %%
import scilayout.grid
reload(scilayout.grid)
reload(scilayout.classes)
reload(scilayout)
plt.close()
fig = scilayout.figure()
fig.set_size_cm(10, 10)
fig.set_location(1500, 50)
# 
fig.clear()
ax = fig.add_panel((1, 1, 6, 6))
ax = fig.add_panel([1, 1, 6, 6])
ax = scilayout.classes.PanelAxes(fig)
fig.add_axes(ax)

scilayout.figure()

# fig.draw_grid()
# fig.grid.hide()
# %%
fig.export('test.png')