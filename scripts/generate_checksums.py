#!/usr/bin/env python3
"""Generate SHA256SUMS.txt from release artifacts.

Format (both human-readable and machine-parseable):

    # SHA256SUMS — STGR Browser <version>
    SHA256 (STGR-Browser-1.0.0-Win64-Setup.exe) = <hex>
    <hex>  STGR-Browser-1.0.0-Win64.zip

Usage:
  python scripts/generate_checksums.py releases
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_checksums(directory: Path, out: Path | None = None) -> Path:
    """Write SHA256SUMS.txt into `directory`. Returns the output path."""
    out = out or directory / "SHA256SUMS.txt"
    files = sorted(p for p in directory.iterdir()
                   if p.is_file() and p.name != out.name)
    lines = [f"# SHA256SUMS — STGR Browser", ""]
    for path in files:
        digest = sha256(path)
        lines.append(f"SHA256 ({path.name}) = {digest}")
        lines.append(f"{digest}  {path.name}")
        lines.append("")
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="generate SHA256SUMS.txt")
    ap.add_argument("directory", type=Path,
                    help="directory containing release artifacts")
    args = ap.parse_args()
    if not args.directory.is_dir():
        print(f"error: {args.directory} is not a directory", file=sys.stderr)
        return 1
    out = write_checksums(args.directory)
    print(f"wrote {out}")
    for line in out.read_text().splitlines():
        if line and not line.startswith("#"):
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
