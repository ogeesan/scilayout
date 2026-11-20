# Changelog

All notable changes to scilayout are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses [EffVer](https://jacobtomlinson.dev/effver/)

## [Unreleased]

### Changed

- Declared the supported dependency versions: matplotlib 3.5 or newer and numpy 1.21.3 or newer.
  The tests pass on these versions, which before were not stated.

## [0.2.0] - 2026-11-20

This release prepares the API for 1.0.
It deprecates how locations are interpreted, so existing code keeps working but now warns.
See [Locations and coordinates](https://ogeesan.github.io/scilayout/coordinates/) for the new terms.

### Deprecated

- Giving a location without a `method` (in `SciFigure.add_panel`, `PanelAxes` and `PanelAxes.set_location`) now emits a `FutureWarning`.
  It is still read as an extent `(x0, y0, x1, y1)`, but the default will change to bounds `(x, y, width, height)` in 1.0.
  Pass `method="extent"` to keep the current behaviour or `method="bounds"` to adopt the new one.
- The `method` values `"bbox"` and `"size"` are deprecated aliases of `"extent"` and `"bounds"`, and will be removed in 1.0.

### Added

- `method="bounds"` and `method="extent"` for reading location tuples.
- `PanelAxes.get_location()` returns an `Extent`, a named tuple `(x0, y0, x1, y1)` that still unpacks like a tuple and holds plain floats.
- `Extent` can be constructed and validates its values (they must be numbers, with `x0 <= x1` and `y0 <= y1`).
- Scale bar text can be centred on the bar with `vpos="center"` (horizontal bars) or `hpos="center"` (vertical bars), leaving a gap in the bar around the text.
  A warning is emitted if the text is longer than the bar, in which case the bar is not drawn.
- The classes can be imported from the top level, for example `scilayout.SciFigure`, `scilayout.ScaleBar` and `scilayout.StatsLine`.
  Every public module defines `__all__`.
- API reference and a page on locations and coordinates in the documentation, built from numpydoc docstrings.
- `pad` option on `ScaleBar` and `LinkedScaleBar` (and a `scalebars.pad` style parameter, 0.1 cm by default): the gap in cm between the edge of the line and the text.
- `Changelog` and `Documentation` links in the package metadata, so they appear on PyPI.
- `savefigure(bbox=None)` (and `SciFigure.export(bbox=None)`) keeps the full figure size instead of cropping tightly.

### Changed

- `PanelLabel.set_alignment()` (and `add_label(ha=...)`) now aligns the label text to its position, with `h` and `v` both applied.
  Before, only `h="right"` did anything, by moving the label 1 cm to the left, and `v` was ignored.
  `add_label` also takes `va`.
- Scale bar text padding is now a fixed distance in cm, measured from the edge of the line, instead of half the height (or width, for vertical bars) of the text.
  It no longer varies with font size or text length, and thick lines push the text away so it never overlaps them.
  For text centred on the bar, the gap in the bar is wider for thicker lines so the visible space around the text is `pad`.
- The minimum Python version is now 3.10.
- Panel labels are positioned further above the panel by default (`panellabel.yoffset` changed from -0.1 to -0.3 cm) so they no longer overlap the top y tick label.
- Invalid options raise `ValueError` rather than failing an `assert`: scale bar `orientation`, `hpos`, `vpos`, `coordSystem` and `transform`, and the length of a panel location.
  `ScaleBar` now rejects an `orientation` that is not `"h"`, `"horizontal"`, `"v"` or `"vertical"` instead of treating it as vertical.
- `SciFigure.clear()` and `clf()` take `keep_observers` like matplotlib, instead of `**kwargs`.
- `ExtentCM`, `BoundCM` and the other unit types are aliases of `Extent` and `Bound`.
- `SciFigure.draw_grid()` takes `major_interval`, `minor_interval` and `half_spacer` and applies them (they were not implemented and warned), and unknown options now raise `TypeError`.
- `SciFigure.set_size_cm()` keeps panels at their location in cm and redraws a shown guide grid, instead of leaving panels at the same fraction of the resized figure.
- `FigureText` takes its default font size, style and weight from the `figuretext.*` style parameters, so its default size is now 8 pt (matplotlib's default is 10 pt).
- `savefigure` logs overwriting at `INFO` level instead of printing.
- `base` and `grid` are documented as internal.
  They are not part of the public API and may change without notice.
- Docstrings use the numpydoc style throughout.

### Fixed

- Eight style parameters were defined but did nothing: `panellabel.fontstyle`, `scalebars.linewidth`, `figuretext.fontsize`, `figuretext.fontstyle`, `figuretext.fontweight`, `stats.linecolor`, `stats.linewidth` and `stats.drop_amount`.
  They are now applied, and a test checks that every parameter is used.
- Removing the guide grid left its axes in the figure, and showing it again added another.
- `ExtentCM(...)` and the other `Extent` types raised `AttributeError` when constructed.
- `ScaleBar` text without a `unit` read "2 None".
- `SciFigure.set_location()` raised `AttributeError` instead of `NotImplementedError` on backends that are not Qt.
- `style.reset()` raised `KeyError` after a parameter had been added.
- Looking up a missing style parameter as an attribute raised `KeyError` rather than `AttributeError`, which broke `hasattr`, and `copy` and `pickle` of the style dictionary failed.
- The return type and documentation of `locationcm_to_position` described the wrong values.

### Removed

- `SciFigure.cm_overlay`, and the code in `set_size_cm()` that called methods which did not exist.
- A debug `print` in `ScaleBar`.
- `ScaleBar.text_pixel_pad_proportion`, replaced by `pad`.
- `base.create_panel_locations`, an internal helper nothing used.

### Development

- Linting with ruff, type checking with pyright, a `justfile`, and a test suite grown from 16 to nearly 600 tests at 100% coverage.
  Examples in docstrings run as doctests, and a test checks that the public API only changes on purpose.
- Visual tests write SVG and PNG figures of a full layout and of scale bar padding, with the expected positions checked against the rendered output.
  Run them with `just visual` (`pytest -m visual --keep-outputs`) to look at the figures in `test_outputs/`.
  Any test that writes figures is marked `visual` automatically.
- Continuous integration runs on Python 3.10 to 3.14 and on macOS and Windows.
  The docs are built with Zensical and published to GitHub Pages, and the build fails on broken links and unresolved cross-references.

## [0.1.2]

See the [release notes](https://github.com/ogeesan/scilayout/releases/tag/v0.1.2).

[Unreleased]: https://github.com/ogeesan/scilayout/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ogeesan/scilayout/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/ogeesan/scilayout/releases/tag/v0.1.2
