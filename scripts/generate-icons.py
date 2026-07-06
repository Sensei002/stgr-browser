#!/usr/bin/env python3
"""
STGR Browser - Icon Generator
Generates all required icon formats from branding/logo.png.

Usage:
    python scripts/generate-icons.py [--logo branding/logo.png] [--output-dir branding]

Requires: Pillow (pip install Pillow)
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image

# Configuration

# Required PNG sizes (from BRANDING.md)
PNG_SIZES = [16, 24, 32, 48, 64, 96, 128, 256, 512]

# ICO files and their included sizes (multi-resolution)
ICO_FILES = {
    "branding/stgr.ico":               [16, 32, 48, 256],
    "branding/installer.ico":          [16, 32, 48, 64, 256],
    "branding/icons/app.ico":          [16, 32, 48, 256],
    "branding/icons/favicon.ico":      [16, 32, 48],
}

# macOS iconset sizes
ICONSET_SIZES = [
    (16, 16, "icon_16x16.png"),
    (32, 32, "icon_16x16@2x.png"),
    (32, 32, "icon_32x32.png"),
    (64, 64, "icon_32x32@2x.png"),
    (128, 128, "icon_128x128.png"),
    (256, 256, "icon_128x128@2x.png"),
    (256, 256, "icon_256x256.png"),
    (512, 512, "icon_256x256@2x.png"),
    (512, 512, "icon_512x512.png"),
    (1024, 1024, "icon_512x512@2x.png"),
]

# Linux icon sizes
LINUX_SIZES = {
    "16x16": 16,
    "22x22": 22,
    "24x24": 24,
    "32x32": 32,
    "48x48": 48,
    "64x64": 64,
    "96x96": 96,
    "128x128": 128,
    "256x256": 256,
}

# Installer image sizes
INSTALLER_IMAGES = {
    "branding/icons/header.bmp":       (150, 57),
    "branding/icons/welcome.bmp":      (164, 314),
    "branding/icons/wix-banner.bmp":   (493, 58),
    "branding/icons/wix-background.bmp": (493, 312),
}


def crop_square(img):
    """Crop the image to the largest centered square."""
    w, h = img.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    return img.crop((left, top, left + size, top + size))


def resize_png(img, size, out_path):
    """Resize and save a single PNG file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(out_path, "PNG")
    print(f"  [OK] {out_path.name} ({size}x{size})")


def make_ico(img, sizes, out_path):
    """Create a multi-resolution ICO file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for size in sizes:
        resized = img.resize((size, size), Image.LANCZOS)
        if resized.mode == "RGBA":
            frames.append(resized)
        else:
            frames.append(resized.convert("RGBA"))

    ico_sizes = [(s, s) for s in sizes if s <= 256]
    frames[0].save(
        out_path,
        format="ICO",
        sizes=ico_sizes,
        append_images=([f for f in frames[1:]] if len(frames) > 1 else []),
    )
    print(f"  [OK] {out_path.name} ({','.join(str(s) for s in sizes)}px)")


def make_iconset(img, iconset_dir):
    """Generate macOS .iconset folder structure."""
    iconset_dir.mkdir(parents=True, exist_ok=True)
    for w, h, filename in ICONSET_SIZES:
        resized = img.resize((w, h), Image.LANCZOS)
        resized.save(iconset_dir / filename, "PNG")
    print(f"  [OK] iconset ({len(ICONSET_SIZES)} files)")


def make_linux_icons(img, linux_dir):
    """Generate Linux icon set in hicolor theme structure."""
    for dirname, size in LINUX_SIZES.items():
        icon_dir = linux_dir / dirname / "apps"
        icon_dir.mkdir(parents=True, exist_ok=True)
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(icon_dir / "stgr-browser.png", "PNG")
    print(f"  [OK] linux icons ({len(LINUX_SIZES)} sizes)")


def make_installer_images(img):
    """Generate installer BMP images from the logo."""
    for path_str, (width, height) in INSTALLER_IMAGES.items():
        out_path = Path(path_str)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        resized = img.resize((width, height), Image.LANCZOS)

        # Convert to BMP (RGB, no alpha for NSIS/WiX compatibility)
        if resized.mode != "RGB":
            bg = Image.new("RGB", (width, height), (10, 10, 10))
            if resized.mode == "RGBA":
                bg.paste(resized, mask=resized.split()[3])
            else:
                bg.paste(resized)
            resized = bg

        resized.save(out_path, "BMP")
        print(f"  [OK] {out_path.name} ({width}x{height})")


def main():
    parser = argparse.ArgumentParser(description="Generate STGR Browser icons from logo.png")
    parser.add_argument("--logo", default="branding/logo.png",
                        help="Path to logo PNG (default: branding/logo.png)")
    parser.add_argument("--output-dir", default="branding",
                        help="Output directory (default: branding)")
    args = parser.parse_args()

    logo_path = Path(args.logo)
    if not logo_path.exists():
        print(f"ERROR: {logo_path} not found!", file=sys.stderr)
        sys.exit(1)

    print(f"Loading logo: {logo_path}")
    img = Image.open(logo_path)
    print(f"  Dimensions: {img.width}x{img.height}, Mode: {img.mode}")

    # Crop to square
    print("\nCropping to square (center)...")
    square = crop_square(img)
    print(f"  Crop size: {square.width}x{square.height}")

    # Step 1: Generate individual PNGs
    print("\n[1/6] Generating PNG files...")
    png_dir = Path(args.output_dir) / "icons" / "png"
    for size in PNG_SIZES:
        resize_png(square, size, png_dir / f"stgr-{size}.png")

    # Also generate a standalone favicon PNG
    resize_png(square, 32, Path(args.output_dir) / "icons" / "favicon.png")

    # Step 2: Generate ICO files
    print("\n[2/6] Generating ICO files...")
    for rel_path, sizes in ICO_FILES.items():
        make_ico(square, sizes, Path(rel_path))

    # Step 3: Generate macOS .iconset
    print("\n[3/6] Generating macOS iconset...")
    iconset_dir = Path(args.output_dir) / "icons" / "stgr.iconset"
    make_iconset(square, iconset_dir)

    # Step 4: Generate Linux icons
    print("\n[4/6] Generating Linux icons...")
    linux_dir = Path(args.output_dir) / "linux"
    make_linux_icons(square, linux_dir)

    # Step 5: Generate installer images
    print("\n[5/6] Generating installer images...")
    make_installer_images(square)

    # Step 6: Generate placeholder files
    print("\n[6/6] Generating reference files...")
    # Create ICNS generation note
    icns_note = Path(args.output_dir) / "icons" / "STGR_ICNS_GENERATION.txt"
    icns_note.write_text(
        "To generate stgr.icns on macOS:\n"
        "  iconutil -c icns branding/icons/stgr.iconset -o branding/stgr.icns\n\n"
        "This requires macOS and cannot be done on Windows.\n"
    )
    print(f"  [OK] Created ICNS generation note")

    # Also copy the largest PNG as a standalone reference
    largest = square.resize((1024, 1024), Image.LANCZOS)
    largest.save(Path(args.output_dir) / "logo-1024.png", "PNG")
    print(f"  [OK] logo-1024.png (reference copy)")

    # Summary
    print("\n" + "=" * 50)
    print("Icon generation complete!")
    print("=" * 50)
    print(f"  PNG files:    {png_dir}/ (x{len(PNG_SIZES)} sizes)")
    print(f"  ICO files:    {len(ICO_FILES)} (multi-res)")
    print(f"  macOS iconset: {iconset_dir}/ ({len(ICONSET_SIZES)} files)")
    print(f"  Linux icons:  {linux_dir}/ ({len(LINUX_SIZES)} sizes)")
    print(f"  Installer:    {len(INSTALLER_IMAGES)} BMP images")
    print(f"\nNote: Run on macOS to convert iconset to .icns:")
    print(f"  iconutil -c icns {iconset_dir} -o branding/stgr.icns")


if __name__ == "__main__":
    main()
