# iPython console: a preferred scientific workflow
Scientists and biologists are commonly introduced to Python with Jupyter Notebooks.
A Jupyter Notebook is a great way to share a demonstration of code and output with other people, but maybe the real reason that Jupyter Notebooks are the starting point is that *it's easy to install and get running quickly*.
This is fine for a course on getting started with Python, but if you are considering making your figures in Python then you will have to move away from a workflow that is dependent on Jupyter Notebooks.

The use of a console and code sections, rather than Notebooks, is better for any larger scale use of Python.
It is also better for full use of Scilayout.

In this guide, I'll explain what a workflow using the other approaches looks like and why I think it's better.

## Interactive figures
Matplotlib has an [interactive mode](https://matplotlib.org/stable/users/explain/figure/interactive.html#interactive-figures).
In this mode, a `matplotlib.Figure` is a literal application window that you can resize and move about your screen.
Most importantly, changes made to the contents of the Figure show up instantly in that window.
Contrast this to Jupyter Notebooks, where the output figure is essentially an image.
To update one particular element of the figure, you have to redraw the entire image.

For example, you can generate a panel and then change the x-limits, the labels, basically any aesthetic element of the plot as long as you know how to interavt with Matplotlib's objects.

`import matplotlib.pyplot as plt` is often used to allow users to `plt.plot()` something.
This approach is meant to mimic MATLAB's plotting library.
However, Matplotlib is built on an object-oriented approach and `pyplot` is for convenience.
The `pyplot` approach has its uses when it comes to rapidly whipping something together, but if you're making figures in Python you *need* to know the OOP approach.

### OOP vs Pyplot
Matplotlib's matplotblog has [a post about OOP vs Pyplot](https://matplotlib.org/matplotblog/posts/pyplot-vs-object-oriented-interface/), which I suggest reading.


## IPython console and code sections


### Sections
In Integrated Development Environments like Spyder, VS Code, and PyCharm, a code section can be denoted with `# %%` (in MATLAB `%%` denotes a section).
A code section is multiple lines that can be run at once via the console.

### Console
The console allows you to make small changes to the figure.
For example, consider a panel that has a `Text` object attached to it.
You may want to modify that object's properties, such as its colour or its position.
A Jupyter Notebook workflow would involve modifying the initialisation of that object, which would mean you running the entire cell again.
However, with the console you're able to punch in to the object itself.
For example, you can use `myaxes.texts` to get a list of all of the `Text` objects in the `Axes`.
If you're using an IDE then using the Tab key you can explore what methods are available (or just consult the relevant documentation).

Specifically for Scilayout, experimenting with different panel locations is very easy because you can change them on the fly.
An even better workflow is if you have a shortcut for running the currently active line in the editor in the console.