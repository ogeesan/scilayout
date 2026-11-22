# Dev notes
## Package structure
```
scilayout/
  scilayout/
    __init__.py
    locations.py
```
## Things to do 
- [ ] Look into Matplotlib transforms and see if a custom transform is what I actually want
  - [ ] https://davidlamb.github.io/2018/07/09/Transformations-Tutorial.html
- [ ] Create unit tests
  - [ ] Meta
    - [ ] Study unit test creation
    - [ ] Choose what must be unit-tested
    - [ ] Work out what kind of coverage I'm after
  - [ ] hashfile of a .png?
    - Subtract the images from each other to find which element is different?
  - [ ] .svg to be used to work out what element has changed?
- [ ] Implement `ScaleBar` and `JointScaleBar`
- [ ] Create useful docs
  - [ ] README.md example
    - [ ] A single image that summarises the approach (i.e. a screenshot of code and figure window side by side)
      - [ ] Source code image
      - [ ] Inkscape to fuse together source code .png and window screenshot
  - [ ] Console example
  - [ ] Jupyter Notebook example
- [ ] Prepare packaging
  - [ ] https://packaging.python.org/en/latest/guides/modernize-setup-py-project/
    - [ ] Build `[project]` table in `pyproject.toml`
      - `dynamic = ["version"]` to read version from `setup.py`, which in turn can be specified in `scilayout.__init__.py`
  - [ ] https://github.com/tomchen/example_pypi_package
    - [ ] Note setup.cfg used to specify version from within `__init__.py`
  - [ ] Social media image
    - [ ] 1280 x 640 image
- [ ] Improve overlay grid
  - [ ] Turn into object?
  - [ ] Configurable markers?
  - [ ] Configurable zorder?
- [ ] Updates on figure repositioning?
- [ ] Documentation
  - Use https://alabaster.readthedocs.io/en/latest/installation.html
  - alabaster is a nice and lightweight readthedocs theme

## Publishing workflow

Build a local thing to check out the docs
```
cd docs
make.bat html
```


- testing
  - `pytest` can't run locally because somethig is really borked with the dependencies, maybe because conda base is so contaminated
  - `unittest` is used locally and can be run with `runtests.bat`
