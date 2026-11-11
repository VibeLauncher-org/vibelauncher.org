"""Checks the contrast of the pairs of colours that the site uses for the text.

The requirement of the site is a contrast of at least 4.5:1 for the body text
and of at least 3:1 for the large text and the borders of the controls.

Run it from the repository root:

    python website/tools/check_contrast.py
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

DARK = {
    "bg": "#0e0d14",
    "surface": "#181624",
    "text": "#e9e7f2",
    "text-muted": "#a6a2b8",
    "text-faint": "#837e99",
    "accent-text": "#b9a4ff",
    "accent": "#8f72fa",
    "on-accent": "#140f24",
    "border-strong": "#6a668c",
}

LIGHT = {
    "bg": "#faf9fd",
    "surface": "#ffffff",
    "text": "#191627",
    "text-muted": "#55516a",
    "text-faint": "#6d6880",
    "accent-text": "#5636c4",
    "accent": "#6b4ce0",
    "on-accent": "#ffffff",
    "border-strong": "#8b88a0",
}

# The pairs that the pages really show: (the text, the background, the ratio
# that is required).
PAIRS = [
    ("text", "bg", 4.5),
    ("text", "surface", 4.5),
    ("text-muted", "bg", 4.5),
    ("text-muted", "surface", 4.5),
    ("text-faint", "bg", 4.5),
    ("text-faint", "surface", 4.5),
    ("accent-text", "bg", 4.5),
    ("accent-text", "surface", 4.5),
    ("on-accent", "accent", 4.5),
    ("border-strong", "bg", 3.0),
]


def channel(value: int) -> float:
    srgb = value / 255
    return srgb / 12.92 if srgb <= 0.04045 else ((srgb + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    raw = hex_colour.lstrip("#")
    r = int(raw[0:2], 16)
    g = int(raw[2:4], 16)
    b = int(raw[4:6], 16)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(first: str, second: str) -> float:
    a = luminance(first)
    b = luminance(second)
    lighter = max(a, b)
    darker = min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def main() -> int:
    failed = False

    for name, palette in (("dark", DARK), ("light", LIGHT)):
        for text, background, required in PAIRS:
            ratio = contrast(palette[text], palette[background])
            mark = "ok  " if ratio >= required else "FAIL"
            if ratio < required:
                failed = True
            print(
                f"{mark} {name:5} {text} on {background}: {ratio:.2f}:1 "
                f"(needs {required}:1)"
            )

    return 1 if failed else 0


def suggest() -> None:
    """Prints the candidates that the palettes may use."""
    candidates = {
        "dark text-faint": ["#837e99", "#88839e", "#8d88a3", "#928da8"],
        "dark border-strong": ["#5c5878", "#636082", "#6a668c", "#716d96"],
        "light text-faint": ["#6d6880", "#67627a", "#615c74", "#5c576e"],
        "light border-strong": ["#8b88a0", "#807d95", "#95929f", "#9a97a8"],
    }
    for label, values in candidates.items():
        print(label)
        for value in values:
            ratios = [f"{contrast(value, bg):.2f}" for bg in ("#0e0d14", "#181624", "#faf9fd", "#ffffff")]
            print(f"    {value}: {' '.join(ratios)}")


if __name__ == "__main__":
    if "--suggest" in sys.argv:
        suggest()
    else:
        sys.exit(main())
