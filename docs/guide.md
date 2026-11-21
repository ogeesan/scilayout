# Guide to building scientific figures

## Image pixels and sizes
When you create a figure (e.g. `plt.figure()`) you're creating a window.
That window exists on the screen.

PPI (Pixels Per Inch) describes the *density* of the pixels.

When we're talking about a figure's "size", we could be refering to a few things.
But here, we're referring to figures in terms of *physical* size.
How the image appears on a screen is only mildly related to the physical size.

### Saving a figure
One of the uses of the figure size is that if you know the physical size constraints you can create the figure with that size, and then work within it on the screen.

One workflow is creating a figure, just sort of vibing the size, exporting a panel, importing it into an image editor, and then trying to make it mesh with the other panels you've got.
This is annoying because the sizing of your text elements, the widths of your lines, and the size of everything is all fixed.
If you want to resize a graph to be larger, then just resizing the image doesn't work.

Instead, regardless of what your workflow is, if you build the your visuals with respect for physical size then it will appear as you expect on a page.
A font of 10 points size is 10 points in size.

## A workflow for saving figures
When you `fig = scilayout.figure()`, the figure 

## Using variables to specify your colours

```python
def plot_mylines(ax) -> None:
    ax.plot(data1)
    ax.plot(data2)

import scilayout
fig = scilayout.figure()
mylines_ax = fig.add_panel()
plot_mylines(mylines_ax)
```

## Saving figures
