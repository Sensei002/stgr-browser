#!/usr/bin/env python3
"""
Guard the single source of truth.

brand.json is consumed by the icon generator, the NTP codegen, the NSIS
installer and the build orchestrator. A missing key shows up as a mysterious
KeyError three jobs later, so validate it up front and fail loudly with a
message that names the exact path.

Run: python scripts/check-brand.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "branding" / "brand.json"

REQUIRED = {
    "product.name": str,
    "product.shortName": str,
    "product.bundleId": str,
    "product.appIdWindows": str,
    "product.protocol": str,
    "product.tagline": str,
    "product.vendor": str,
    "product.homepage": str,
    "product.repository": str,
    "product.copyright": str,
    "versions.initial": str,
    "versions.channel": str,
    "colors.red": str,
    "colors.redBright": str,
    "colors.redDeep": str,
    "colors.gold": str,
    "colors.black": str,
    "colors.surface": str,
    "colors.surfaceAlt": str,
    "colors.border": str,
    "colors.text": str,
    "colors.muted": str,
    "assets.logoMaster": str,
    "assets.iconIco": str,
    "assets.iconIcns": str,
    "assets.logoTrimmed": str,
    "assets.ntpLogo": str,
    "urls.defaultSearchEngine": str,
    "features.adBlocker": bool,
    "features.telemetry": bool,
    "features.extensions": bool,
}


def get(data: dict, dotted: str):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(dotted)
        node = node[part]
    return node


def main() -> int:
    if not BRAND.exists():
        print(f"error: {BRAND} missing", file=sys.stderr)
        return 1

    try:
        data = json.loads(BRAND.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: brand.json is not valid JSON: {exc}", file=sys.stderr)
        return 1

    problems: list[str] = []

    for path, expected in REQUIRED.items():
        try:
            value = get(data, path)
        except KeyError:
            problems.append(f"missing: {path}")
            continue
        if not isinstance(value, expected):
            problems.append(f"{path} should be {expected.__name__}, got {type(value).__name__}")
            continue
        if isinstance(value, str) and not value.strip():
            problems.append(f"{path} is empty")

    # Colour values must be usable as CSS and as NSIS/RGB triples.
    for key in ("red", "redBright", "redDeep", "gold", "black", "surface", "surfaceAlt", "border", "text", "muted"):
        try:
            value = get(data, f"colors.{key}")
        except KeyError:
            continue
        if not (value.startswith("#") and len(value) == 7):
            problems.append(f"colors.{key} must be #RRGGBB, got {value!r}")

    # Assets must exist on disk.
    for key in ("logoMaster", "logoTrimmed", "iconIco", "iconIcns", "ntpLogo"):
        try:
            rel = get(data, f"assets.{key}")
        except KeyError:
            continue
        if not (ROOT / rel).exists():
            problems.append(f"assets.{key} points at a missing file: {rel}")

    # Speed dial sanity: 5-6 tiles keep the grid on one row.
    dial = data.get("speedDial")
    if not isinstance(dial, list) or not dial:
        problems.append("speedDial must be a non-empty list")
    else:
        if not 1 <= len(dial) <= 6:
            problems.append(f"speedDial has {len(dial)} entries; the NTP grid fits at most 6")
        for index, item in enumerate(dial):
            for field in ("label", "url", "icon"):
                if not item.get(field):
                    problems.append(f"speedDial[{index}].{field} is missing")

    if problems:
        print("brand.json validation failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"brand.json ok: {data['product']['name']} v{data['versions']['initial']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
