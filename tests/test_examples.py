"""The documentation examples build, so the images in the README and docs stay current."""

import warnings
from pathlib import Path

import pytest
from matplotlib.figure import Figure

import scilayout

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = sorted((ROOT / "examples").glob("[!_]*.py"))


def load_build_images():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_images", ROOT / "scripts" / "build_images.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_there_are_examples():
    assert EXAMPLES


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.stem)
def test_example_builds_without_warnings(example, tmp_path):
    build_images = load_build_images()
    with warnings.catch_warnings():
        # the examples show current usage, so they must not rely on anything deprecated
        warnings.simplefilter("error")
        written = build_images.build(example, tmp_path)
    assert written
    for path in written:
        assert path.stat().st_size > 0
        assert path.suffix in {".png", ".svg"}


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.stem)
def test_example_makes_a_scifigure(example):
    import runpy

    module = runpy.run_path(str(example))
    fig = module["make"]()
    assert isinstance(fig, scilayout.SciFigure)
    assert isinstance(fig, Figure)
    assert module.get("FORMATS", ("png",))
    fig.clear()
