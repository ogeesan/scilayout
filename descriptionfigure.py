"""Create demonstration figure

"""
# %%
import matplotlib.pyplot as plt
import numpy as np

import scilayout
# %%
fig = scilayout.figure()

# %%
fig.clear()
"""
The idea is to create a single image that summarises scilayout's power.
Each line of code could be colour-coded if it adds an element to the figure.
"""
# %% Create axes

fig.set_size_cm(18, 15)
fig.clear()
fig.draw_grid()
ax_code = fig.add_panel((.1, 1, 7, 5))
ax = ax_code
ax.set_yticks([])
ax.set_xticks([])
codestrings = [("fig = scilayout.figure()", 'black'),
               ('# build panel', 'grey'),
               ("ax = fig.add_panel((10, .5, 15, 5.5))", 'purple'),
               ("ax.plot(np.linspace(0, 1, 100),\n        np.sin(2 * np.pi * np.linspace(0, 1, 100)))", 'blue'),
               ("ax.add_label('B')", 'red'),
               ("ax.add_scalebar()", 'green'),
               ('\n# %% move panel B', 'grey'),
               ("ax.set_location((13.6, 2.1, 1.5, 1.8), method='size')", 'orange'),
               ('\n# %% adjust scalebar', 'grey'),
               ("ax.scalebar.set_location((13.6, 2.1))", 'brown'),
               ]
# TODO: update scalebar to matched syntax
ypos = 1
for text, color in codestrings:
    textobj = ax.text(0, ypos, text, color=color, ha='left', va='top', fontsize=8, family='monospace', transform=ax.transAxes)
    
    # update ypos based on size of text object
    nlines = text.count('\n') + 1
    ypos -= nlines * 0.08

ax_code.axis('off')

ax_mainexample = fig.add_panel((9.7, .5, 15, 4.5), 'b')
fig.grid.hide()
ax_mainexample.axis('off')

# set axis color to red with params context
with plt.rc_context({'axes.edgecolor': 'purple', 'axes.linewidth': 2}):
    ax_output = fig.add_panel((6, 1, 11, 5))
# ax_example_output = fig.add_panel((6, 1, 11, 5))
ax_output.plot(np.linspace(0, 1, 100), np.sin(2 * np.pi * np.linspace(0, 1, 100)), color='blue')
ax_output.add_label('B')
ax_output.panellabel.text.set_color('red')
ax_output.set_yticks([])
ax_output.set_xticks([])

with plt.rc_context({'axes.edgecolor': 'orange', 'axes.linewidth': 2}):
    ax_output_moved = fig.add_panel((8, 3.5, 9.5, 5))
ax_output_moved.plot(np.linspace(0, 1, 100), np.sin(2 * np.pi * np.linspace(0, 1, 100)), color='orange')
ax_output_moved.add_label('B')
ax_output_moved.panellabel.text.set_color('orange')
ax_output_moved.set_yticks([])
ax_output_moved.set_xticks([])


# TODO: add something which indicates the cm positions of things

# % Set layout
ax_code.set_location((.1, .5, 7, 5))
ax_code.add_label('a')
ax_code.panellabel.set_location(x=.1, y=.4)

ax_output.set_location((10, 1, 3, 3), method='size')
ax_output_moved.set_location((13.6, 2.1, 1.5, 1.8), method='size')


# %% Save example
fig.add_overlay()
ax = fig.cm_overlay
ax.clear()
height_width = scilayout.locations.inch_to_cm(fig.get_size_inches())
ax.set_xlim(0, height_width[0])
ax.set_ylim(height_width[1], 0)
ax.plot([3.8, 10], [1.1, .4], c='grey', ls='--', lw=.5)
ax.plot([10, 10], [.4, 5], c='grey', ls=':')
ax.text(10, 5, '10 cm from left side', color='grey', va='top')
# add a scalebar for the cm

# %% Save the figure