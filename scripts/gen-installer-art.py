#!/usr/bin/env python3
"""
Generate the NSIS wizard bitmaps from the brand palette.

Outputs (committed, because NSIS needs 24-bit BMP and we do not want a font
dependency in CI):
    overrides/windows/wizard.bmp   164x314  welcome/finish left panel
    overrides/windows/header.bmp   150x57   inner page header

Deliberately text-free: the installer pages already carry the copy, and shapes
+ logo stay reproducible on any machine without system fonts.

Run: python scripts/gen-installer-art.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "overrides" / "windows"


def hex_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return tuple(int(v[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    w, h = size
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    a, b = hex_rgb(top), hex_rgb(bottom)
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[index]
    return strip.resize((w, h), Image.Resampling.BILINEAR)


def add_slashes(img: Image.Image, color: str, specs: list[tuple[int, int, int, int]]) -> None:
    """specs: (x0, y0, dx, height) parallelograms leaning right."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r, g, b = hex_rgb(color)
    for x0, y0, dx, h in specs:
        width = max(dx // 4, 6)
        d.polygon(
            [(x0, y0), (x0 + width, y0), (x0 + width - dx, y0 + h), (x0 - dx, y0 + h)],
            fill=(r, g, b, 46),
        )
    img.alpha_composite(overlay)


def build() -> None:
    brand = json.loads((ROOT / "branding" / "brand.json").read_text(encoding="utf-8"))
    colors = brand["colors"]
    logo = Image.open(ROOT / brand["assets"]["logoTrimmed"]).convert("RGBA")

    # ── wizard panel 164x314 ────────────────────────────────────────────────
    w, h = 164, 314
    base = gradient((w, h), "#131319", colors["black"]).convert("RGBA")
    add_slashes(base, colors["red"], [(150, -20, 90, 190), (120, -20, 60, 120)])

    mark_w = 118
    mark = logo.resize((mark_w, round(logo.height * mark_w / logo.width)), Image.Resampling.LANCZOS)
    base.alpha_composite(mark, ((w - mark.width) // 2, 108))

    rule = Image.new("RGBA", (w, 2), (255, 255, 255, 22))
    base.alpha_composite(rule, (0, 100))

    OUT.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(OUT / "wizard.bmp", format="BMP")

    # ── header strip 150x57 ─────────────────────────────────────────────────
    hw, hh = 150, 57
    head = gradient((hw, hh), "#141419", colors["black"]).convert("RGBA")
    add_slashes(head, colors["red"], [(140, -10, 60, 90)])
    small = logo.resize((46, round(logo.height * 46 / logo.width)), Image.Resampling.LANCZOS)
    head.alpha_composite(small, (8, (hh - small.height) // 2))
    head.convert("RGB").save(OUT / "header.bmp", format="BMP")

    print("installer art written: wizard.bmp, header.bmp")


if __name__ == "__main__":
    build()
