#!/usr/bin/env python3
"""Compute the next release version for the STGR CI/CD pipeline.

The version lives in stgr/config/stgr-config.json (single source of truth).
The release workflow calls this on every push to main and bumps the PATCH
component past the highest existing vX.Y.Z tag, so each merged commit
produces a fresh release (auto tag + auto version bump).

Usage:
  python scripts/next_version.py            # print next version, e.g. 1.0.1
  python scripts/next_version.py --write    # ... and write it back to the config
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "stgr" / "config" / "stgr-config.json"

_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def parse_version(text: str) -> tuple[int, int, int] | None:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", text.strip())
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def highest_tag() -> tuple[int, int, int] | None:
    """Highest existing vX.Y.Z tag, or None when no release tags exist."""
    try:
        out = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return None
    versions = []
    for tag in out.splitlines():
        m = _TAG_RE.match(tag.strip())
        if m:
            versions.append(tuple(int(x) for x in m.groups()))
    return max(versions) if versions else None


def next_version(config_version: str,
                 tag_version: tuple[int, int, int] | None) -> str:
    """Bump past the highest tag; the config wins only when already ahead.

    A config version equal to the highest tag must still bump (the tag already
    exists and `gh release create` would fail), so the check is strict >.
    """
    cfg = parse_version(config_version)
    if tag_version is None:
        return config_version if cfg else "0.1.0"
    if cfg and cfg > tag_version:
        return config_version
    major, minor, patch = tag_version
    return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="write the bumped version back into stgr-config.json")
    args = ap.parse_args()

    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    current = data["product"]["version"]
    new = next_version(current, highest_tag())

    if args.write:
        data["product"]["version"] = new
        CONFIG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
