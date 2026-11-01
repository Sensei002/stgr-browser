#!/usr/bin/env python3
"""
STGR Browser - brand asset generator.

Produces every icon format the build pipeline needs, from one master logo:

    branding/icons/logo-trimmed.png     transparent, tightly cropped logo
    branding/icons/png/<n>.png          16..1024 px application icons
    branding/icons/stgr.ico             Windows multi-resolution icon
    branding/icons/stgr.icns            macOS icon bundle
    branding/icons/macos/<n>.png        macOS squircle masters
    ntp/assets/logo.png                 logo used by the New Tab Page

Run:  python branding/generate-icons.py
CI:   called from .github/workflows/ci.yml to prove the assets are reproducible.

Requires: Pillow >= 10
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
BRANDING = ROOT / "branding"
ICONS = BRANDING / "icons"

# Rendered canvas sizes. 1024 is the master everything is downsampled from.
PNG_SIZES = [16, 24, 32, 48, 64, 128, 256, 512, 1024]
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
ICNS_MAP = [
    ("icp4", 16),
    ("icp5", 32),
    ("icp6", 64),
    ("ic07", 128),
    ("ic08", 256),
    ("ic09", 512),
    ("ic10", 1024),
    ("ic11", 32),
    ("ic12", 64),
    ("ic13", 256),
    ("ic14", 512),
]

MASTER = 1024


def load_brand() -> dict:
    with open(BRANDING / "brand.json", encoding="utf-8") as fh:
        return json.load(fh)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def trimmed_logo(source: Path) -> Image.Image:
    """Crop the sticker-white margin so the mark sits optically centred."""
    im = Image.open(source).convert("RGBA")
    bbox = im.split()[3].getbbox()
    if bbox:
        im = im.crop(bbox)
    return im


def vertical_gradient(size: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    grad = Image.new("RGB", (1, size))
    px = grad.load()
    for y in range(size):
        t = y / max(size - 1, 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))  # type: ignore[index]
    return grad.resize((size, size), Image.Resampling.BILINEAR)


def squircle(size: int, radius_ratio: float) -> Image.Image:
    """Anti-aliased rounded square mask, supersampled 4x then reduced."""
    ss = 4
    mask = Image.new("L", (size * ss, size * ss), 0)
    draw = ImageDraw.Draw(mask)
    r = int(size * ss * radius_ratio)
    draw.rounded_rectangle([0, 0, size * ss - 1, size * ss - 1], radius=r, fill=255)
    return mask.resize((size, size), Image.Resampling.LANCZOS)


def compose(
    logo: Image.Image,
    brand: dict,
    *,
    inset_ratio: float,
    radius_ratio: float,
    logo_ratio: float,
    logo_shift: float = 0.0,
) -> Image.Image:
    """Build a square app icon: gradient plate + centred logo."""
    canvas = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))

    plate_size = int(MASTER * (1 - inset_ratio * 2))
    plate = vertical_gradient(plate_size, hex_rgb("#1A1A20"), hex_rgb(brand["colors"]["black"]))
    plate = plate.convert("RGBA")
    plate.putalpha(squircle(plate_size, radius_ratio))

    # 1px-ish inner highlight so the plate reads as a surface, not a hole.
    edge = Image.new("RGBA", (plate_size, plate_size), (0, 0, 0, 0))
    d = ImageDraw.Draw(edge)
    d.rounded_rectangle(
        [1, 1, plate_size - 2, plate_size - 2],
        radius=int(plate_size * radius_ratio),
        outline=(255, 255, 255, 26),
        width=max(1, plate_size // 340),
    )
    plate = Image.alpha_composite(plate, edge)

    offset = (MASTER - plate_size) // 2
    canvas.alpha_composite(plate, (offset, offset))

    # Scale the mark to a fixed fraction of the canvas width.
    target_w = int(MASTER * logo_ratio)
    scale = target_w / logo.width
    target_h = int(logo.height * scale)
    mark = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

    x = (MASTER - target_w) // 2
    y = (MASTER - target_h) // 2 + int(MASTER * logo_shift)
    canvas.alpha_composite(mark, (x, y))
    return canvas


def write_png_set(master: Image.Image, out_dir: Path, sizes: list[int]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for size in sizes:
        resized = master.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(out_dir / f"{size}.png", optimize=True)


def write_ico(master: Image.Image, path: Path, sizes: list[int]) -> None:
    """Hand-rolled ICO writer: PNG payloads keep the file small and crisp."""
    payloads = []
    for size in sizes:
        buf = path.parent / f".tmp-{size}.png"
        master.resize((size, size), Image.Resampling.LANCZOS).save(buf, format="PNG", optimize=True)
        payloads.append((size, buf.read_bytes()))
        buf.unlink()

    header = struct.pack("<HHH", 0, 1, len(payloads))
    offset = len(header) + 16 * len(payloads)
    entries = b""
    body = b""
    for size, data in payloads:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset)
        body += data
        offset += len(data)

    path.write_bytes(header + entries + body)


def write_icns(master: Image.Image, path: Path) -> None:
    chunks = b""
    for ostype, size in ICNS_MAP:
        buf = path.parent / f".tmp-{ostype}.png"
        master.resize((size, size), Image.Resampling.LANCZOS).save(buf, format="PNG", optimize=True)
        data = buf.read_bytes()
        buf.unlink()
        chunks += ostype.encode("ascii") + struct.pack(">I", len(data) + 8) + data

    path.write_bytes(b"icns" + struct.pack(">I", len(chunks) + 8) + chunks)


def main() -> int:
    brand = load_brand()
    source = ROOT / brand["assets"]["logoMaster"]
    if not source.exists():
        print(f"error: master logo missing at {source}", file=sys.stderr)
        return 1

    logo = trimmed_logo(source)
    logo.save(ICONS / "logo-trimmed.png", optimize=True)

    # Desktop / Linux / Windows icon: tight plate, generous mark.
    desktop = compose(logo, brand, inset_ratio=0.02, radius_ratio=0.18, logo_ratio=0.80)
    write_png_set(desktop, ICONS / "png", PNG_SIZES)
    write_ico(desktop, ICONS / "stgr.ico", ICO_SIZES)

    # macOS: Apple's grid wants a ~10% margin and a 22.37% corner radius.
    mac = compose(logo, brand, inset_ratio=0.10, radius_ratio=0.2237, logo_ratio=0.68)
    write_png_set(mac, ICONS / "macos", PNG_SIZES)
    write_icns(mac, ICONS / "stgr.icns")

    # NTP hero: keep the mark on transparency, it sits on a photo background.
    ntp_target = ROOT / brand["assets"]["ntpLogo"]
    ntp_target.parent.mkdir(parents=True, exist_ok=True)
    hero = logo.copy()
    hero.thumbnail((720, 720), Image.Resampling.LANCZOS)
    hero.save(ntp_target, optimize=True)

    print(f"icons written: {len(PNG_SIZES)} png + ico + icns + ntp hero")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
