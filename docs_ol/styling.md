# Styling your plots
Matplotlib has the ability to [use custom stylesheets to configure plot aesthetics](https://matplotlib.org/stable/users/explain/customizing.html#customizing-with-style-sheets).
Rather than have to specify every detail of your plot each time you create an element (e.g. the font, colour, size etc. of your x-tick labels), you can modify the "default" settings that will be used when you create an item.


For a consistent visual style users can set options for views in a few ways.

`scilayout.style.py` contains the code required to modify styles.

## Methods
### 1. Using a stylesheet
Matplotlib has a concept of a stylesheet, a text file which defines basically every parameter used to generate a plot.
This is how you can have a different style for a paper versus a dark-mode presentation.
Scilayout supports a similar approach using JSON files.

```json
{
    "scalebars.linewidth": 6,
    "scalebars.color": 'white',
}
```

Scilayout uses a similar setup to Matplotlib's `plt.style.use('path/to/stylefile.mplstyle')`.

```python
import scilayout

scilayout.style.use('path/to/jsonfile.json')  # load and apply styles

```


### 2. Setting parameters of objects directly
For more flexibility and overriding of style behaviour, you can specify parameters much like parameters used for other system.
Maybe you want to style things for a particular plot differently to the others.
All of the parameters set using `scilayout.style` can be modified at the creation or updated after the creation of a scilayout object.

```python
import scilayout

```

### 3. Using your own `figures` module
A project may make use of a specific style, and one way to modify that is to use a figures module.
I'm not saying that this is the best practice way to do it, but it is a way you can do it.

```python
# * Inside myproject/figures.py
from scilayout import *
import scilayout
scilayout.style.params['scalebars.color'] = 'white'

```