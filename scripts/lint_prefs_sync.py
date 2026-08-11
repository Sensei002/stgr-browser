#!/usr/bin/env python3
"""Pref-sync linter (runs without a Firefox checkout).

Extracts the `// BEGIN STGR … PREFS` … `// END STGR` blocks from the canonical
files in stgr/config/preferences/ and from the STGR patches, and asserts they
match exactly. Prevents drift between the preference layer and the patch
series — CI runs this on every PR.

Exit code 0 = in sync, 1 = drift detected.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows CI pipes stdout as cp1252, which cannot encode the ✅/❌ status
# glyphs printed below — force UTF-8 so the lint never dies on encoding
# (Python 3.7+; harmless elsewhere).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
PREFS_DIR = ROOT / "stgr" / "config" / "preferences"
PATCHES_DIR = ROOT / "patches"

MARKER = re.compile(r"// (BEGIN STGR [A-Z ]*PREFS|END STGR)")


def extract_blocks(text: str, is_patch: bool = False) -> dict:
    """Return {marker: [lines]} for each BEGIN…END block in a file.

    When `is_patch` is True, unified-diff added lines carry a leading '+'
    which must be stripped *before* matching the marker lines — otherwise
    the block is never opened.
    """
    blocks, current = {}, None
    for line in text.splitlines():
        if is_patch and line.startswith("+"):
            line = line[1:]
        m = MARKER.search(line)
        if m and line.startswith("// BEGIN STGR"):
            current = m.group(1)
            blocks[current] = []
        elif m and line.startswith("// END STGR") and current:
            blocks[current].append(line)
            current = None
        elif current is not None:
            blocks[current].append(line)
    return blocks


def canonical_blocks() -> dict:
    merged = {}
    for file in sorted(PREFS_DIR.glob("*.js")):
        for marker, lines in extract_blocks(file.read_text(encoding="utf-8")).items():
            merged.setdefault(marker, []).extend(lines)
    return merged


def patch_blocks() -> dict:
    merged = {}
    for file in sorted(PATCHES_DIR.glob("*.patch")):
        text = file.read_text(encoding="utf-8")
        for marker, lines in extract_blocks(text, is_patch=True).items():
            merged.setdefault(marker, []).extend(lines)
    return merged


def main() -> int:
    canonical = canonical_blocks()
    patched = patch_blocks()
    failures = 0

    for marker in sorted(set(canonical) | set(patched)):
        if marker not in canonical:
            print(f"  ❌ {marker}: in patches but missing from canonical files")
            failures += 1
            continue
        if marker not in patched:
            print(f"  ❌ {marker}: in canonical files but missing from patches")
            failures += 1
            continue
        if canonical[marker] != patched[marker]:
            print(f"  ❌ {marker}: canonical and patch blocks differ")
            failures += 1
        else:
            print(f"  ✅ {marker} ({len(canonical[marker])} lines, in sync)")

    if failures:
        print("PREF SYNC DRIFT DETECTED — update the patch alongside the "
              "canonical preference file.")
        return 1
    print("pref sync OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
