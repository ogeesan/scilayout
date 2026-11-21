# Locations and coordinates

Scilayout places things on a figure in **centimetres from its upper left corner**, the way you would measure a layout on a page, instead of in matplotlib's figure fractions.

![A 12 by 7 cm figure with a centimetre grid, showing the x axis pointing right and the y axis pointing down from the upper left corner, and a panel at (1.5, 1.5) that is 4.5 cm wide and 2.5 cm high](images/coordinates.svg)

??? example "Code for this figure"

    ```python
    --8<-- "examples/coordinates.py"
    ```

- The origin is the **upper left** of the figure.
- `y` increases **downwards**.
  This is the opposite of matplotlib's data and figure coordinates, where `y` increases upwards.
- Everything that takes a position in cm uses this convention: panels, panel labels, figure text and `cm` scalebar positions.

## Describing a rectangle

A rectangle, such as a panel, can be described in two ways.
Scilayout calls them *bounds* and *extent*, which are the same words matplotlib uses for `Bbox.bounds` and `Bbox.extents`.

| | Values | Meaning | Name |
| --- | --- | --- | --- |
| **bounds** | `(x, y, w, h)` | upper left corner, then width and height | [`Bound`][scilayout.types.Bound] |
| **extent** | `(x0, y0, x1, y1)` | upper left corner, then lower right corner | [`Extent`][scilayout.types.Extent] |

These two panels are the same:

```python
import scilayout

fig = scilayout.figure()
fig.set_size_cm(12, 8)

fig.add_panel((1.5, 1.5, 4.5, 2.5), method="bounds")  # x, y, width, height
fig.add_panel((1.5, 1.5, 6.0, 4.0), method="extent")  # x0, y0, x1, y1
```

Use bounds when you know how big a panel should be, for example a journal column width.
Use extents when you want to line edges up with something else.

## The `method` argument

[`SciFigure.add_panel`][scilayout.classes.SciFigure.add_panel], [`PanelAxes`][scilayout.classes.PanelAxes] and [`PanelAxes.set_location`][scilayout.classes.PanelAxes.set_location] take a location tuple and a `method` that says how to read it:

| `method` | Reads the tuple as |
| --- | --- |
| `"bounds"` | `(x, y, width, height)` |
| `"extent"` | `(x0, y0, x1, y1)` |

Bounds with a negative width or height, and extents whose corners are the wrong way round, raise a `ValueError`.

!!! warning "The default is changing"

    If you don't give a `method`, a location is currently read as an **extent**, and scilayout emits a `FutureWarning`.
    In version 1.0 the default will change to **bounds**.
    Pass `method="extent"` to keep your current behaviour, or `method="bounds"` to adopt the new one.
    Either removes the warning.

    The older names `"bbox"` (now `"extent"`) and `"size"` (now `"bounds"`) still work but are deprecated, and will be removed in version 1.0.

## Reading a location back

[`PanelAxes.get_location`][scilayout.classes.PanelAxes.get_location] always returns an [`Extent`][scilayout.types.Extent], whichever way the panel was created.
It is a named tuple, so it unpacks like one and its fields can be read by name:

```python
ax = fig.add_panel((1.5, 1.5, 4.5, 2.5), method="bounds")

x0, y0, x1, y1 = ax.get_location()
ax.get_location().x1  # 6.0
```

## Converting between units

[`scilayout.locations`][scilayout.locations] has the conversions that scilayout uses itself.
For example, [`cm_to_fraction`][scilayout.locations.cm_to_fraction] and [`fraction_to_cm`][scilayout.locations.fraction_to_cm] move between cm from the upper left and matplotlib's figure fraction.

## Placing artists in cm

`fig.transCM` is a matplotlib transform from cm (from the upper left) to the figure.
Pass it as `transform` to place any artist in cm, the way you would use `ax.transAxes`:

```python
fig.text(2, 1, "2 cm across, 1 cm down", transform=fig.transCM)
```

It follows the figure when its size changes, and combines with other transforms.
[`CMTransform`][scilayout.locations.CMTransform] is the same transform but ends at figure fractions, so `CMTransform(fig) + fig.transFigure` is equivalent to `fig.transCM`.
