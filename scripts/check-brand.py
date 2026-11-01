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


def extension_id_from_key(key_b64: str) -> str:
    """
    Chromium extension ID = first 128 bits of SHA-256 over the DER public key,
    hex-encoded, with each hex digit mapped 0-f -> a-p.
    """
    import base64
    import hashlib

    der = base64.b64decode(key_b64)
    digest = hashlib.sha256(der).hexdigest()[:32]
    return "".join(chr(ord("a") + int(c, 16)) for c in digest)


def check_newtab_wiring(data: dict, problems: list[str]) -> None:
    """
    The new-tab URL appears in four places: the NTP manifest key (which derives
    the ID), brand.json, the seeded preferences and the enterprise policy. If
    they drift, the browser silently falls back to Chromium's built-in new tab
    page - which is exactly the bug this check exists to prevent.
    """
    manifest_path = ROOT / "ntp" / "manifest.json"
    prefs_path = ROOT / "config" / "preferences" / "stgr-defaults.json"
    policy_path = ROOT / "config" / "policies" / "base.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        problems.append(f"cannot read ntp/manifest.json: {exc}")
        return

    key = manifest.get("key")
    if not key:
        problems.append("ntp/manifest.json has no 'key' - the extension ID would not be stable")
        return

    try:
        actual_id = extension_id_from_key(key)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"ntp/manifest.json 'key' is not valid base64: {exc}")
        return

    declared_id = data.get("extensions", {}).get("ntpId")
    if declared_id != actual_id:
        problems.append(
            f"extensions.ntpId is {declared_id!r} but the manifest key derives {actual_id!r}"
        )

    expected_url = f"chrome-extension://{actual_id}/index.html"
    for label, value in (
        ("extensions.ntpUrl", data.get("extensions", {}).get("ntpUrl")),
        ("urls.newTab", data.get("urls", {}).get("newTab")),
    ):
        if value != expected_url:
            problems.append(f"{label} should be {expected_url!r}, got {value!r}")

    try:
        prefs = json.loads(prefs_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        problems.append(f"cannot read preferences: {exc}")
    else:
        if prefs.get("homepage") != expected_url:
            problems.append(f"preferences homepage should be {expected_url!r}, got {prefs.get('homepage')!r}")
        session = prefs.get("session", {})
        # 5 = "open the New Tab Page". Chromium filters chrome-extension:// URLs
        # out of startup_urls, so an explicit URL list would silently do nothing.
        if session.get("restore_on_startup") != 5:
            problems.append("preferences session.restore_on_startup should be 5 (open the new tab page)")
        if session.get("startup_urls"):
            problems.append("preferences session.startup_urls must stay empty - Chromium filters chrome-extension:// from it")
        if "newtab_page_location_override" in prefs:
            problems.append(
                "newtab_page_location_override must not be set - pointing it at stgr:// is what "
                "made the first tab fall back to the built-in new tab page"
            )

    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        problems.append(f"cannot read policies: {exc}")
    else:
        if policy.get("HomepageLocation") != expected_url:
            problems.append("policy HomepageLocation does not match the new-tab URL")


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

    check_newtab_wiring(data, problems)
    if problems:
        print("new-tab wiring is inconsistent:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"brand.json ok: {data['product']['name']} v{data['versions']['initial']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
