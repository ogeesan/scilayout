"""Examples in docstrings must run, and the documented style must be consistent."""

import doctest
import importlib
import inspect
import re

import matplotlib.pyplot as plt
import pytest

MODULES = [
    "scilayout",
    "scilayout.classes",
    "scilayout.locations",
    "scilayout.scalebars",
    "scilayout.stats",
    "scilayout.style",
    "scilayout.types",
]
ALL_MODULES = [*MODULES, "scilayout.base", "scilayout.grid"]


@pytest.mark.parametrize("name", MODULES)
def test_docstring_examples_run(name):
    module = importlib.import_module(name)
    result = doctest.testmod(
        module, optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    )
    plt.close("all")
    assert result.failed == 0


def documented_objects():
    """Every class, function and method defined in scilayout with its docstring."""
    for name in ALL_MODULES:
        module = importlib.import_module(name)
        for attr, obj in vars(module).items():
            if getattr(obj, "__module__", None) != module.__name__:
                continue
            if inspect.isfunction(obj) or inspect.isclass(obj):
                yield f"{name}.{attr}", obj
            if inspect.isclass(obj):
                for method_name, method in vars(obj).items():
                    if inspect.isfunction(method):
                        yield f"{name}.{attr}.{method_name}", method


@pytest.mark.parametrize(("name", "obj"), list(documented_objects()))
def test_docstrings_use_numpy_style_not_sphinx_fields(name, obj):
    doc = inspect.getdoc(obj) or ""
    assert not re.search(
        r"^\s*:(param|type|return|rtype|raises)\b", doc, re.MULTILINE
    ), f"{name} uses Sphinx-style fields, use numpydoc Parameters/Returns sections"
