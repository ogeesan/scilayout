"""Build the images used by the README and the documentation.

Each ``examples/*.py`` script defines ``make()``, which returns a figure, and
``FORMATS``, the file formats to save it in. The images are written to
``docs/images/`` (not committed), which becomes ``images/`` on the documentation site.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
IMAGES = ROOT / "docs" / "images"


def build(example: Path, out_dir: Path = IMAGES) -> list[Path]:
    """Run one example and save its figure in each of its formats."""
    module = runpy.run_path(str(example))
    fig = module["make"]()
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for fmt in module.get("FORMATS", ("png",)):
        path = out_dir / f"{example.stem}.{fmt}"
        # opaque white, so the image is readable on dark pages as well as light ones
        # SVG text as paths, so it looks the same without the font installed
        with plt.rc_context({"svg.fonttype": "path"}):
            fig.savefig(path, dpi=200, facecolor="white", transparent=False)
        written.append(path)
    plt.close(fig)
    return written


def main() -> int:
    """Build every example."""
    examples = sorted(p for p in EXAMPLES.glob("*.py") if not p.name.startswith("_"))
    for example in examples:
        for path in build(example):
            print(f"{example.name} -> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
