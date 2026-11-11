"""Builds the binary assets of the site: the web fonts and the Open Graph image.

The fonts of the launcher are shipped as variable TTF files of about 800 KB each.
A page that loads them as they are is far too heavy, so the glyphs are cut down
to the ones the site uses and packed into WOFF2.

Run it from the repository root:

    python website/tools/build_assets.py

The script writes into `website/assets/fonts` and `website/assets/img`.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

from fontTools import ttLib
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE_FONTS = ROOT / "assets" / "fonts"
SITE = ROOT / "website"
TARGET_FONTS = SITE / "assets" / "fonts"
TARGET_IMG = SITE / "assets" / "img"

# The characters of the site: the printable ASCII and everything that the pages
# and the stylesheets of the site use. Cutting the fonts down to them is what
# keeps the page light.
EXTRA_CHARS = "→·—–…‘’“”«»×©°"

# The weights the stylesheets ask for. A font that keeps a wider axis than the
# site needs only makes the file bigger.
FONTS = [
    ("Inter-Variable.ttf", "inter.woff2", (400, 700)),
    ("Archivo-Variable.ttf", "archivo.woff2", (600, 600)),
    ("GeistMono-Variable.ttf", "geist-mono.woff2", (400, 500)),
]


def characters_of_the_site() -> set[str]:
    """Collects every character that the site shows."""
    chars: set[str] = set(chr(code) for code in range(0x20, 0x7F))
    chars.update(EXTRA_CHARS)

    for path in sorted(SITE.rglob("*.html")) + sorted(SITE.rglob("*.css")):
        text = path.read_text(encoding="utf-8")
        # The tags and the attributes of the HTML carry no letters for the reader.
        text = re.sub(r"<[^>]*>", " ", text)
        chars.update(text)

    return {char for char in chars if char.isprintable() and char not in "\t\n\r"}


def subset(source: pathlib.Path, target: pathlib.Path, chars: set[str], weights: tuple[int, int]) -> None:
    """Cuts the glyphs of one variable font down and packs it into WOFF2."""
    text = "".join(sorted(chars))
    low, high = weights

    with tempfile.TemporaryDirectory() as folder:
        cut = pathlib.Path(folder) / "cut.ttf"

        font = ttLib.TTFont(str(source))
        axes = {axis.axisTag for axis in font["fvar"].axes}
        limits = {"wght": (low, high)} if "wght" in axes else {}
        if limits:
            font = instancer.instantiateVariableFont(font, limits, inplace=True)
        font.save(str(cut))
        font.close()

        command = [
            sys.executable,
            "-m",
            "fontTools.subset",
            str(cut),
            f"--output-file={target}",
            "--flavor=woff2",
            f"--text={text}",
            "--layout-features=kern,liga,calt,ccmp,locl,mark,mkmk",
            "--name-IDs=*",
            "--no-hinting",
            "--desubroutinize",
            "--drop-tables+=DSIG",
        ]
        subprocess.run(command, check=True)


def main() -> None:
    TARGET_FONTS.mkdir(parents=True, exist_ok=True)
    chars = characters_of_the_site()
    print(f"the site uses {len(chars)} characters")

    for source_name, target_name, weights in FONTS:
        source = SOURCE_FONTS / source_name
        if not source.is_file():
            sys.exit(f"missing font: {source}")
        target = TARGET_FONTS / target_name
        subset(source, target, chars, weights)
        print(f"{target_name}: {target.stat().st_size // 1024} KB")

    og = TARGET_IMG / "og.png"
    if og.is_file():
        print(f"og.png: {og.stat().st_size // 1024} KB (already built)")


if __name__ == "__main__":
    main()
