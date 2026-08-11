#!/usr/bin/env python3
"""Generate the STGR icon set from the master logo.

Inputs (priority order):
  1. stgr/branding/stgr-logo.png  — raster master (>=512x512)
  2. stgr/branding/stgr-logo.svg  — vector master (requires cairosvg)

Non-square masters (e.g. the official 2048x1728 SVG) are center-fitted onto a
square canvas with transparent padding — never distorted or cropped.

Outputs (stgr/branding/icons/):
  icon-{16,24,32,48,64,128,256,512}.png
  stgr.ico  (multi-resolution Windows icon)

--generate-placeholder  draws a simple stand-in logo with the standard library
                        so the pipeline can be tested before the official logo
                        is provided. Never ship placeholder icons.

Pillow is required for resizing/ICO. `pip install pillow`.
"""
from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "stgr" / "branding"
ICONS = BRAND / "icons"
SIZES = [16, 24, 32, 48, 64, 128, 256, 512]


def error(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


# ── Pure-stdlib placeholder PNG writer ──────────────────────────────
def _chunk(tag: bytes, data: bytes) -> bytes:
    c = struct.pack(">I", len(data)) + tag + data
    c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return c


def _png(rgba: list, width: int, height: int) -> bytes:
    raw = b"".join(b"\x00" + bytes(v) for v in rgba)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(raw, 9))
            + _chunk(b"IEND", b""))


def draw_placeholder(size: int) -> bytes:
    """Dark square with a red 'roof' wedge and gold band (stand-in only)."""
    black = (8, 8, 8, 255)
    red = (232, 32, 42, 255)
    dark_red = (143, 16, 24, 255)
    gold = (200, 164, 93, 255)
    px = []
    for y in range(size):
        for x in range(size):
            # rounded-corner mask
            r = size * 0.08
            in_corner = (x < r and y < r) or (x > size - r and y < r) \
                or (x < r and y > size - r) or (x > size - r and y > size - r)
            c = black
            if not in_corner:
                # pagoda roof wedge
                if y < size * 0.42:
                    t = 1 - abs((x - size / 2) / (size / 2))
                    if y < (1 - t) * size * 0.42:
                        c = red if t > 0.25 else dark_red
                    elif y < (1 - t) * size * 0.42 + size * 0.06:
                        c = gold
                # red body block
                elif y < size * 0.62:
                    if size * 0.3 < x < size * 0.7:
                        c = red
            px.append(c)
    return _png(px, size, size)


# ── Loader ──────────────────────────────────────────────────────────
def fit_square(img) -> "Image.Image":
    """Center a non-square master onto a square canvas (transparent padding).

    `img` must be RGBA; both callers convert before calling.
    """
    if img.width == img.height:
        return img
    side = max(img.width, img.height)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    print(f"note: master is {img.width}x{img.height} (non-square); "
          "centered with transparent padding")
    return canvas


def load_master(placeholder: bool) -> tuple:
    try:
        from PIL import Image
    except ImportError:
        error("Pillow is required for icon generation. `pip install pillow`")

    if placeholder:
        master = Image.frombytes("RGBA", (512, 512),
                                 draw_placeholder(512)).convert("RGBA")
        print("using generated placeholder (dev only — never ship)")
    else:
        png = BRAND / "stgr-logo.png"
        svg = BRAND / "stgr-logo.svg"
        if png.exists():
            master = Image.open(png).convert("RGBA")
        elif svg.exists():
            try:
                import cairosvg  # type: ignore
            except ImportError:
                error("master PNG missing and cairosvg not installed. "
                      "Provide stgr/branding/stgr-logo.png (>=512x512) or "
                      "`pip install cairosvg`.")
            # Render at native aspect ratio (output_width only — cairosvg
            # preserves the SVG's height proportionally), then square it up.
            import io
            png_bytes = cairosvg.svg2png(url=str(svg), output_width=2048)
            master = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        else:
            error(f"no master logo. Provide {png} (>=512x512) or {svg}. "
                  "Use --generate-placeholder to test the pipeline.")
        master = fit_square(master)
    if min(master.size) < 256:
        print(f"warning: master logo is small ({master.size}); "
              "512x512+ recommended")
    return master


def generate(master, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        img = master.resize((size, size), 3)  # LANCZOS
        img.save(out / f"icon-{size}.png", "PNG")
        print(f"  wrote icon-{size}.png")

    ico = master.resize((256, 256), 3)
    ico.save(out / "stgr.ico", format="ICO",
             sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    print("  wrote stgr.ico")


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR icon generator")
    ap.add_argument("--generate-placeholder", action="store_true",
                    help="test the pipeline with a generated stand-in logo")
    args = ap.parse_args()
    master = load_master(args.generate_placeholder)
    generate(master, ICONS)
    print(f"icons written to {ICONS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
