= An example of image embedding
`scilayout` builds figures in their native size, meaning that no image stretching is required for the figure to appear exactly as described in the code.
```python
import scilayout
fig = scilayout.figure()

ax_sine = fig.add_panel((1, 1, 4, 5), method='size)
```

// #raw(read("figurescript.py"), lang: "python")
#image("../social-media-preview.svg")