[![PyPI version](https://img.shields.io/pypi/v/scilayout)](https://pypi.org/project/scilayout/) [![Tests](https://github.com/ogeesan/scilayout/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ogeesan/scilayout/actions/workflows/tests.yml) ![Pepy Total Downloads](https://img.shields.io/pepy/dt/scilayout) [![Coverage Status](https://coveralls.io/repos/github/ogeesan/scilayout/badge.svg?branch=main)](https://coveralls.io/github/ogeesan/scilayout?branch=main)
[![matplotlib 3.5+](https://img.shields.io/badge/matplotlib-%E2%89%A5%203.5-blue)](https://matplotlib.org) [![Compatibility](https://github.com/ogeesan/scilayout/actions/workflows/compat.yml/badge.svg?branch=main)](https://github.com/ogeesan/scilayout/actions/workflows/compat.yml) [![EffVer Versioning](https://img.shields.io/badge/version_scheme-EffVer-0097a7)](https://jacobtomlinson.dev/effver)

# What is `scilayout`?

> [!WARNING]  
> This package is in beta.

`pip install scilayout`

Scilayout is a Python package to make creating multi-panel scientific figures easier, faster, and maybe a little bit more fun. The core idea is to build figures using coordinates in **centimetres from the top left** using interactive plotting. This approach has a few main benefits:

1. The iterative process of building figures up from scratch is easier.
2. Complex layouts can be interchanged more easily.
3. Exported figure sizes are explicitly stated (in centimetres) for seamless embedding in documents.

There are many guides for Matplotlib styling for scientific publication, and there are a number of packages that make this process easier (e.g. [SciencePlots](https://github.com/garrettj403/SciencePlots)), but this `scilayout` supports the creation of figures which are 100% ready for embedding in documents.

![A figure with three panels laid out with scilayout](https://ogeesan.github.io/scilayout/images/hero.png)

Panel a is the global mean temperature over the Common Era from the [PAGES2k Consortium reconstruction](https://doi.org/10.1038/s41561-019-0400-0) (Neukom et al., 2019).
The data in panels b and c are made up.

```python
import scilayout

fig = scilayout.figure()  # it's a matplotlib figure like plt.figure()

# creates a 5 x 5 cm panel with its upper left corner 1 cm from the left and 1 cm from the top
myax = fig.add_panel((1, 1, 5, 5), method="bounds")  # (x, y, width, height)

# %%
# move the panel after it's been created: now 5 x 3 cm, 2 cm from the left and 10 cm from the top
myax.set_location((2, 10, 5, 3), method="bounds")
# or give the upper left and lower right corners (x0, y0, x1, y1) instead
myax.set_location((2, 10, 7, 13), method="extent")
```

This package is designed for people with:
- A basic understanding of `matplotlib`'s `Axes` object and how to work with it (rather than only using `plt`, the differences described [here](https://matplotlib.org/matplotblog/posts/pyplot-vs-object-oriented-interface/))
- A desire to produce figures entirely in code (example approaches described in blogposts from [brushingupscience.com](https://brushingupscience.com/2021/11/02/a-better-way-to-code-up-scientific-figures/#more-6299) and [dendwrite.substack](https://dendwrite.substack.com/p/a-complete-ish-guide-to-making-scientific))

<!-- show documentation site at ogeesan.github.io/scilayout centered and heading size -->
<div align="center">
  <h2><a href="https://ogeesan.github.io/scilayout">Documentation Site (github.io/scilayout)</a></h2>
</div>
