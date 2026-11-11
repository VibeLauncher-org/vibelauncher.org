"""Checks the HTML of the site: the parser of html5 must find no error.

Run it from the repository root:

    python website/tools/check_html.py
"""

from __future__ import annotations

import pathlib
import sys

import html5lib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = ROOT / "website"


def main() -> int:
    failed = False

    for page in sorted(SITE.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        parser = html5lib.HTMLParser(strict=False)
        parser.parse(text)

        if parser.errors:
            failed = True
            print(f"{page.name}: {len(parser.errors)} errors")
            for error in parser.errors[:10]:
                print(f"    {error}")
        else:
            print(f"{page.name}: valid")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
