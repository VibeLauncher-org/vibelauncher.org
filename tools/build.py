"""Assembles the site into the folder that is published: `website/dist`.

The source folder holds the tools and the README; they stay in the repository
and do not go to the server. The result is a plain folder with `index.html` at
its root, which is what the publishing step expects.

Run it from the repository root:

    python website/tools/build.py
"""

from __future__ import annotations

import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = ROOT / "website"
DIST = SITE / "dist"

# What goes to the server: the pages and the assets they need.
PAGES = ["index.html", "download.html", "privacy.html", "404.html"]
FILES = ["robots.txt", "sitemap.xml"]
DIRECTORIES = ["assets"]


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)

    DIST.mkdir(parents=True)

    for name in PAGES + FILES:
        source = SITE / name
        if not source.is_file():
            sys.exit(f"missing page: {source}")
        shutil.copy2(source, DIST / name)

    for name in DIRECTORIES:
        source = SITE / name
        if not source.is_dir():
            sys.exit(f"missing directory: {source}")
        shutil.copytree(source, DIST / name)

    index = DIST / "index.html"
    if not index.is_file():
        sys.exit("the build has no index.html at its root")

    total = sum(path.stat().st_size for path in DIST.rglob("*") if path.is_file())
    count = sum(1 for path in DIST.rglob("*") if path.is_file())
    print(f"the build is in {DIST}: {count} files, {total // 1024} KB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
