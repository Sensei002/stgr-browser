#!/usr/bin/env python3
"""Generate the non-Mozilla image assets required by Firefox's Windows NSIS build.

Firefox's browser/installer/windows/Makefile.in expects these files in the
branding directory. They are generated into the staged in-tree branding copy,
so no Mozilla installer artwork is redistributed:

  firefox64.ico
  document.ico / newwindow.ico / newtab.ico / pbmode.ico / document_pdf.ico
  stubinstaller/bgstub.jpg
  wizHeader.bmp
  wizHeaderRTL.bmp
  wizWatermark.bmp

The application icon is the official STGR-derived stgr.ico. The BMPs use the
STGR black/red/gold visual system and are intentionally dependency-free.
"""
from __future__ import annotations

import argparse
import base64
import shutil
import struct
from pathlib import Path

# Valid 1x1 JPEG used only for the legacy stub-installer background input.
# The x64 release build does not enable Mozilla's optional stub installer.
BLACK_JPEG = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////"
    "////////////////////////////////////////////////////////2wBDAf//////////////////////////////"
    "////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAA"
    "AAAAAAAAAAAABf/EABQQAQAAAAAAAAAAAAAAAAAAAAA/2gAMAwEAAhADEAAAAf/EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEA"
    "AT8hP//EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQIBAT8QH//EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QH//Z"
)


def _bmp(path: Path, width: int, height: int, rtl: bool = False) -> None:
    """Write a 24-bit bottom-up BMP with STGR geometric accent bands."""
    rows = []
    row_padding = (4 - (width * 3) % 4) % 4
    for y in range(height):
        row = bytearray()
        visual_y = height - 1 - y
        for x in range(width):
            xx = width - 1 - x if rtl else x
            # Quiet black base with a subtle vertical red gradient.
            red = 8 + int(18 * visual_y / max(height - 1, 1))
            green = 8
            blue = 8
            # Angular dojo mark and restrained gold accent.
            center = width // 2
            roof = max(0, int((height * 0.58) - abs(xx - center) * 0.52))
            if visual_y < roof:
                red, green, blue = 110, 12, 20
            if abs(visual_y - int(height * 0.63)) <= max(1, height // 45):
                red, green, blue = 200, 164, 93
            if abs(xx - center) <= max(1, width // 28) and visual_y > int(height * 0.3):
                red, green, blue = 232, 32, 42
            row.extend((blue, green, red))
        row.extend(b"\0" * row_padding)
        rows.append(bytes(row))

    pixel_data = b"".join(rows)
    file_header = struct.pack("<2sIHHI", b"BM", 14 + 40 + len(pixel_data), 0, 0, 54)
    dib = struct.pack(
        "<IIIHHIIIIII", width, height, 1, 24, 0, len(pixel_data),
        2835, 2835, 0, 0, 0
    )
    path.write_bytes(file_header + dib + pixel_data)


def generate(out: Path, icon: Path) -> None:
    if not icon.is_file():
        raise SystemExit(f"STGR icon is missing: {icon}")
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(icon, out / "firefox64.ico")

    # Firefox's Windows .rc resources hard-reference the full application icon
    # set from the branding directory (firefox.exe.rc, private_browsing.exe.rc);
    # llvm-rc fails if any are missing. All variants derive from the STGR
    # master icon.
    for name in ("document.ico", "newwindow.ico", "newtab.ico",
                 "pbmode.ico", "document_pdf.ico"):
        shutil.copy2(icon, out / name)

    _bmp(out / "wizHeader.bmp", 150, 57)
    _bmp(out / "wizHeaderRTL.bmp", 150, 57, rtl=True)
    _bmp(out / "wizWatermark.bmp", 164, 314)

    stub = out / "stubinstaller"
    stub.mkdir(parents=True, exist_ok=True)
    (stub / "bgstub.jpg").write_bytes(base64.b64decode(BLACK_JPEG))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--icon", type=Path, required=True)
    args = parser.parse_args()
    generate(args.output, args.icon)
    print(f"installer branding assets generated in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
