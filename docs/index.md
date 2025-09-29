---
hide:
  - navigation
---
# scilayout
<!-- ![Image of scilayout](../social-media-preview.svg) -->

Scilayout is a Python package to assist in making multi-panel scientific figures.
It aims to make laying out figures easy, fast, and maybe even fun.
The idea is simply to make and interact with Matplotlib axes in centimetres from the top left, which when combined with existing interactive plotting tools makes building plots in Python a breeze.

```python
import scilayout

# Create a figure object
fig = scilayout.figure()

# Create a panel, specifying location in cm from top left
myax = fig.add_panel((1, 1, 5, 5))

# %% Panel setup 1
# move the panel after it's been created and set it's location based on size
myax.set_location((2, 10, 3, 3), method='size')

# %% Panel setup 2


```

## Getting started
Install onto your machine with `pip install scilayout`.

### How much Python do you need to know to make use of this?
To make full use of Scilayout, there are two things a user should know about.

1. Interactive plotting
2. Matplotlib's object-oriented approach

The first is interactive plotting with iPython, which allows users to modify figures on the fly.
The second is matplotlib's object-oriented approach, which allows users to create and modify multiple plots at once.

#### Matplotlib's object-oriented interface
Scilayout is built to work with the object-oriented component of matplotlib. If this means nothing to you, or you exclusively use `plt.plot`, then it's worth thinking about using with Matplotlib's `Axes` objects directly.

You are ready to use scilayout when you are able to write a function that takes an existing `matplotlib.Axes` object as one of its arguments, and the function draws the plot

```python
def mydataplot(ax, data):
    ax.plot(data.x, data.y)
    ax.set_title('My glorious title')
    ax.set_xlabel('Time spent learning matplotlib')
    ax.set_ylabel('Time required to create suitable graphs')
```

## Considerations

### Downsides to using Python to make your figures
Vector graphhic formats are not perfectly standardised, and so sometimes there are odd rendering issues if you export from Python but read using Inkscape/Illustrator.
This can depend on which backend is used?

Collaboration using .pdf figures can be painful. If only one user is using Python to make the figures but their collaborators are not, then the Python user would have to replicate their changes in code.

## Why use this?

1. Vector graphics are the way to go
2. Python and Matplotlib are very flexible and transferable
3. Iterative figure design is fast and fun
4. Version control and portability

Vector graphics are higher resolution, more portable, and easier to edit.
Where possible, we should use vector graphics.

Iterative figure design is where it's at.


You can integrate your figures with version control tools like Git entirely.

### Why I use scilayout
Personally, I don't want to be importing data into Python for manipulation/analysis, exporting into Excel, fiddling with the format and then forwarding it on to another tool like Prism. The handling of data outside of a code-context makes me nervous.

Using scilayout, I can stay entirely within an environment that is entirely text based while still making some great looking figures.

## Further reading 
- [A guide to making your own figure](./making_your_own_figure.md)
- [A guide to plot styling](./styling.md)

- Python Graph Gallery's website
- Python Graph Gallery's [guide to Matplotlib](https://python-graph-gallery.com/matplotlib/): an excellent way to tie together your understanding of the various elements of Matplotlib once you have a handle on the basics.

I highly recommend checking out [plottools](https://github.com/bendalab/plottools) by Jan Benda.
plottools is a full-fledged add-on for matplotlib, although it isn't optimised for Live Plotting.
Check out [their documentation](https://bendalab.github.io/plottools/), the Tutorial section being of high relevance to anyone interested in figure generation in Python, with/without scilayout/plottools.