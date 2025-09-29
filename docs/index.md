---
hide:
  - navigation
---
# scilayout
<!-- ![Image of scilayout](../social-media-preview.svg) -->

Scilayout is a Python package to assist in making multi-panel scientific figures.
It aims to make laying out figures easy, fast, and maybe even fun.
The idea is to make and interact with Matplotlib axes in centimetres from the top left, which when combined with existing interactive plotting tools makes building plots in Python a breeze.

```python title="Example usage"
>>> import scilayout

# Create a figure object
>>> fig = scilayout.figure()

# Create a panel, specifying location in cm from top left
>>> myax = fig.add_panel((1, 1, 5, 5))

# move the panel after it's been created and set it's location based on size
>>> myax.set_location((2, 10, 3, 3), method='size')

```

## Why use this?

1. Powerful figure design: there are practically no limits when it comes to building figures with Matplotlib
2. Universal skills: rather than learning proprietary software you can learn flexible and transferable Python and Matplotlib skills.
3. Text based source: version control, portability, and fiddling are as easy as managing text files.
6. Vector graphics: make use of Matplotlib's renderer to gain huge flexibility of quality output.

## Getting started
### Installation
Install onto your machine with `pip install scilayout`, or if you're using uv (1) `uv add scilayout`.
{ .annotate }

1. [uv](https://docs.astral.sh/uv/) is like pip but very (confusingly) fast and lovely to use.
   Make the jump over for your next project!

### How much Python do you need to know to make use of this?
To make full use of Scilayout, there are two things a user should know about.

1. [Interactive plotting](https://matplotlib.org/stable/users/explain/figure/interactive.html): iPython consoles support live figures that make prototyping figures and fiddling with the look easy and responsive.
2. [Matplotlib's object-oriented approach](https://matplotlib.org/matplotblog/posts/pyplot-vs-object-oriented-interface/): an alternative way of using Matplotlib that unlocks more complex customisation.


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

### Downsides to using Python to make your figures
Vector graphhic formats are not perfectly standardised, and so sometimes there are odd rendering issues if you export from Python but read using Inkscape/Illustrator.
A guide on potential pitfalls are forthcoming.

Collaboration using .pdf figures can be painful.
If only one user is using Python to make the figures but their collaborators are not, then the Python user would have to replicate their changes in code.

## Further reading 
<!-- - [A guide to making your own figure](./making_your_own_figure.md) -->
<!-- - [A guide to plot styling](./styling.md) -->

- Scientific figure generation
    - [plottools](https://github.com/bendalab/plottools) by Jan Benda: various utility functions to help build scientific figures
    - [plottools documentation](https://bendalab.github.io/plottools/): the Tutorial section being of high relevance to anyone interested in figure generation in Python, with/without scilayout/plottools.
    - [brushingupscience.com blog post](https://brushingupscience.com/2021/11/02/a-better-way-to-code-up-scientific-figures/#more-6299): using functions to build scientific figures
    - [dendwrite.substack's block post](https://dendwrite.substack.com/p/a-complete-ish-guide-to-making-scientific): building scientific figures from start to finish
- Working with Matplotlib
    - [Python Graph Gallery](https://python-graph-gallery.com/): various applications of Matplotlib
    - Python Graph Gallery's [guide to Matplotlib](https://python-graph-gallery.com/matplotlib/): an excellent way to tie together your understanding of the various elements of Matplotlib once you have a handle on the basics.
    - [matplotlib's guide to pyplot vs object-oriented interface](https://matplotlib.org/matplotblog/posts/pyplot-vs-object-oriented-interface/): necessary reading to understand how to plot without relying on `plt`
