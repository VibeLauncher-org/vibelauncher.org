"""Builds the Open Graph image of the site: 1200x630 pixels, dark background,
the mark of the launcher and the wordmark.

The image is composed here instead of being drawn by hand: the mark comes from
the repository as an SVG, the text is set with the fonts of the project.

Run it from the repository root:

    python website/tools/build_og.py
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE_ICONS = ROOT / "assets" / "icons"
SOURCE_FONTS = ROOT / "assets" / "fonts"
TARGET = ROOT / "website" / "assets" / "img" / "og.png"

WIDTH = 1200
HEIGHT = 630

BACKGROUND = (14, 13, 20)
TEXT = (233, 231, 242)
MUTED = (166, 162, 184)
ACCENT = (143, 114, 250)


def render_mark() -> Image.Image:
    """Renders the mark of the launcher into a PNG of 320 pixels."""
    rsvg = shutil.which("rsvg-convert")
    if rsvg is None:
        sys.exit("rsvg-convert is not on the path")

    with tempfile.TemporaryDirectory() as folder:
        target = pathlib.Path(folder) / "mark.png"
        subprocess.run(
            [
                rsvg,
                "--width",
                "320",
                "--height",
                "320",
                "--output",
                str(target),
                str(SOURCE_ICONS / "mark.svg"),
            ],
            check=True,
        )

        with Image.open(target) as image:
            return image.convert("RGBA")


def font(path: pathlib.Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def render_icon(size: int) -> Image.Image:
    """Renders the icon of the launcher into a PNG of the given size."""
    rsvg = shutil.which("rsvg-convert")
    if rsvg is None:
        sys.exit("rsvg-convert is not on the path")

    with tempfile.TemporaryDirectory() as folder:
        target = pathlib.Path(folder) / "icon.png"
        subprocess.run(
            [
                rsvg,
                "--width",
                str(size),
                "--height",
                str(size),
                "--output",
                str(target),
                str(SOURCE_ICONS / "icon.svg"),
            ],
            check=True,
        )

        with Image.open(target) as image:
            return image.convert("RGBA")


def build_favicon() -> None:
    """Writes the favicon of the site: the icon at 16, 32 and 48 pixels."""
    target = ROOT / "website" / "assets" / "icons" / "favicon.ico"
    sizes = [(16, 16), (32, 32), (48, 48)]
    images = [render_icon(size) for size, _ in sizes]
    images[0].save(target, format="ICO", sizes=sizes)
    print(f"favicon.ico: {target.stat().st_size // 1024} KB")


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    # A soft glow of the accent behind the mark, so the frame is not flat.
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((60, 60, 460, 460), fill=(*ACCENT, 40))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(image)

    mark = render_mark()
    image.paste(mark, (88, 155), mark)

    wordmark = font(SOURCE_FONTS / "Archivo-Variable.ttf", 96)
    tagline = font(SOURCE_FONTS / "Inter-Variable.ttf", 38)
    note = font(SOURCE_FONTS / "GeistMono-Variable.ttf", 26)

    x = 448
    draw.text((x, 190), "VibeLauncher", font=wordmark, fill=TEXT)
    draw.text((x, 320), "A Minecraft launcher written in Rust", font=tagline, fill=MUTED)
    draw.text((x, 400), "No telemetry. No servers of its own.", font=note, fill=ACCENT)

    image.save(TARGET, "PNG", optimize=True)
    print(f"og.png: {TARGET.stat().st_size // 1024} KB, {image.width}x{image.height}")

    build_favicon()


if __name__ == "__main__":
    main()
