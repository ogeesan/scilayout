"""Internal helpers."""

import inspect
from pathlib import Path

_PACKAGE_DIR = str(Path(__file__).parent)


def find_stack_level() -> int:
    """Find the ``stacklevel`` that makes a warning point at the caller's own code.

    Walks out of the frames inside scilayout, so the warning blames the line in the
    user's script however many scilayout functions it passed through.
    """
    # Counting starts at this function's own frame, which is one deeper than the
    # function that calls warnings.warn (stacklevel 1), so the count lands on the caller.
    frame = inspect.currentframe()
    level = 0
    while frame is not None and frame.f_code.co_filename.startswith(_PACKAGE_DIR):
        frame = frame.f_back
        level += 1
    return level
