"""Fail if the built docs contain Markdown syntax that was not processed.

``zensical build --strict`` reports dead links between pages but not cross-references
like ``[text][scilayout.classes.SciFigure]`` that don't resolve: those are left in the
page as literal text. The same goes for collapsible blocks (``???``) and snippet
includes (``--8<--``) when their extension is missing or the syntax is mangled.
Run this after building to catch them.

    python scripts/check_site.py [site_dir]
"""

import html
import re
import sys
from pathlib import Path

# [text][dotted.path] that was left as text, e.g. "[set_location][scilayout.x.y]"
UNRESOLVED = re.compile(r"\]\[(?:scilayout|matplotlib|numpy|builtins)[\w.]*\]")
# a ??? block or --8<-- snippet that was left as text
UNPROCESSED = re.compile(r"^\?\?\?\+? \w+|--8\s*<\s*--", re.MULTILINE)
TAGS = re.compile(r"<[^>]+>")


def unresolved_references(site: Path) -> list[tuple[Path, str]]:
    """Find (page, text) for every unresolved cross-reference in the built site."""
    found = []
    for page in sorted(site.rglob("*.html")):
        text = TAGS.sub("", page.read_text(encoding="utf-8"))
        for match in UNRESOLVED.finditer(text):
            start = max(text.rfind("[", 0, match.start()), match.start() - 60)
            found.append((page, text[start : match.end()].strip()))
    return found


def unprocessed_syntax(site: Path) -> list[tuple[Path, str]]:
    """Find (page, text) for every ``???`` block or snippet include left as text."""
    found = []
    for page in sorted(site.rglob("*.html")):
        text = html.unescape(TAGS.sub("", page.read_text(encoding="utf-8")))
        found.extend((page, m.group(0)) for m in UNPROCESSED.finditer(text))
    return found


def main() -> int:
    """Check the site, print what is wrong, and return the exit code."""
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    if not site.is_dir():
        print(f"{site} not found: build the docs first")
        return 2
    problems = unresolved_references(site)
    for page, reference in problems:
        print(f"{page.relative_to(site)}: unresolved reference {reference!r}")
    if problems:
        print(f"{len(problems)} unresolved cross-reference(s)")
    leftovers = unprocessed_syntax(site)
    for page, text in leftovers:
        print(f"{page.relative_to(site)}: Markdown syntax left as text {text!r}")
    return 1 if problems or leftovers else 0


if __name__ == "__main__":
    sys.exit(main())
