#!/usr/bin/env python3
"""
STGR Browser - Splash Screen Generator
Generates assets/splash-screen.svg with the actual logo.png embedded as base64.

Usage:
    python scripts/generate-splash.py [--logo branding/logo.png] [--output assets/splash-screen.svg]
    python scripts/generate-splash.py --logo branding/logo.png --output assets/splash-screen.svg

Requires: Pillow (pip install Pillow)
"""

import os
import sys
import base64
import argparse
from pathlib import Path
from PIL import Image
from io import BytesIO

# ── Splash Screen Template ─────────────────────────────────────────────────────
# This is an SVG splash screen (800x600) with:
#   - Dark background with subtle grid overlay
#   - Actual logo.png centered (resized to a nice display size)
#   - Animated loading bar
#   - "STGR BROWSER" title text
#   - "STARTING..." subtitle
#   - Version info at bottom
#
# Colors follow the dark red + black STGR palette:
#   Background: #0A0A0A → #0D0D0D gradient
#   Accent:     #C41E3A (cardinal red)
#   Secondary:  #8B0000 (dark red)
#   Glow:       #FF4444 (bright red)
#   Text:       #E8E8E8
#   Muted:      #909090

SPLASH_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 800 600" fill="none">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0A0A0A;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0D0D0D;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="loadGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FF4444;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#C41E3A;stop-opacity:1" />
    </linearGradient>

    <!-- Drop shadow for the logo -->
    <filter id="logoShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="12" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="800" height="600" fill="url(#bgGrad)" />

  <!-- Subtle grid pattern for tech/gaming feel -->
  <g opacity="0.03" stroke="white" stroke-width="0.5">
    <line x1="0" y1="200" x2="800" y2="200" />
    <line x1="0" y1="400" x2="800" y2="400" />
    <line x1="200" y1="0" x2="200" y2="600" />
    <line x1="400" y1="0" x2="400" y2="600" />
    <line x1="600" y1="0" x2="600" y2="600" />
  </g>

  <!-- Subtle radial glow behind the logo -->
  <radialGradient id="glowGrad" cx="50%" cy="50%" r="50%">
    <stop offset="0%" style="stop-color:#C41E3A;stop-opacity:0.08" />
    <stop offset="100%" style="stop-color:#C41E3A;stop-opacity:0" />
  </radialGradient>
  <circle cx="400" cy="240" r="160" fill="url(#glowGrad)" />

  <!-- Actual logo from branding/logo.png (embedded as base64) -->
  <g filter="url(#logoShadow)">
    <image xlink:href="data:image/png;base64,LOGO_BASE64"
           x="300" y="140" width="200" height="200"
           preserveAspectRatio="xMidYMid meet" />
  </g>

  <!-- Loading bar background -->
  <rect x="250" y="380" width="300" height="3" rx="1.5" fill="#1E1E1E" />

  <!-- Animated loading bar -->
  <rect x="250" y="380" width="0" height="3" rx="1.5" fill="url(#loadGrad)">
    <animate attributeName="width" values="0;120;200;280;300" dur="3s" fill="freeze" />
  </rect>

  <!-- Title -->
  <text x="400" y="420" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="24" font-weight="700" fill="#E8E8E8" letter-spacing="4">
    STGR BROWSER
  </text>

  <!-- Subtitle -->
  <text x="400" y="445" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="12" font-weight="500" fill="#909090" letter-spacing="2">
    STARTING...
  </text>

  <!-- Version -->
  <text x="400" y="560" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="10" fill="#505050">
    Version {version} — Based on Mozilla Gecko
  </text>
</svg>
'''


def get_logo_base64(logo_path, size=200):
    """
    Read logo.png, resize to fit the splash screen, and return as base64 data URI.

    The logo is resized to `size` pixels on its longest edge while maintaining
    aspect ratio, so it fits within the splash screen's logo area (200x200 box).
    """
    img = Image.open(logo_path).convert("RGBA")

    # Resize to fit within the display area
    img.thumbnail((size, size), Image.LANCZOS)

    # Create a square canvas (centered) for consistent placement
    square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    square.paste(img, offset, mask=img.split()[3])

    # Save to bytes as PNG
    buf = BytesIO()
    square.save(buf, format="PNG")
    buf.seek(0)

    # Encode as base64
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return b64


def get_version():
    """Get the version from branding config or return default."""
    config_path = Path("branding/branding-config.json")
    if config_path.exists():
        try:
            import json
            with open(config_path) as f:
                config = json.load(f)
            return config.get("build", {}).get("applicationVersion", "1.0.0")
        except (json.JSONDecodeError, KeyError):
            pass
    return "1.0.0"


def main():
    parser = argparse.ArgumentParser(
        description="Generate STGR Browser splash screen with actual logo")
    parser.add_argument("--logo", default="branding/logo.png",
                        help="Path to logo PNG (default: branding/logo.png)")
    parser.add_argument("--output", default="assets/splash-screen.svg",
                        help="Output SVG path (default: assets/splash-screen.svg)")
    parser.add_argument("--logo-size", type=int, default=200,
                        help="Logo display size in SVG units (default: 200)")
    args = parser.parse_args()

    logo_path = Path(args.logo)
    if not logo_path.exists():
        print(f"ERROR: {logo_path} not found!", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading logo: {logo_path}")
    logo_b64 = get_logo_base64(logo_path, args.logo_size)
    version = get_version()

    # Generate the splash SVG
    svg_content = SPLASH_TEMPLATE.replace("LOGO_BASE64", logo_b64)
    svg_content = svg_content.replace("{version}", version)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"\nSplash screen generated: {output_path}")
    print(f"  Logo size: {args.logo_size}x{args.logo_size} (SVG units)")
    print(f"  Logo base64: {len(logo_b64)} chars")
    print(f"  Version: {version}")
    print(f"  SVG file: {output_path} ({os.path.getsize(output_path)} bytes)")


if __name__ == "__main__":
    main()
