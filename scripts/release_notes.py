#!/usr/bin/env python3
"""Generate GitHub release notes for STGR Browser (§69).

Pulls the STGR version, the Firefox base version, and the commit history
since the previous tag. Run by release.yml; also usable locally.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config  # noqa: E402


def git_log_since(previous_tag: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", "--oneline", "--no-merges",
             f"{previous_tag}..HEAD" if previous_tag else "HEAD"],
            cwd=ROOT, capture_output=True, text=True, check=True)
        return out.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []


def main() -> int:
    ap = argparse.ArgumentParser(description="generate STGR release notes")
    ap.add_argument("version", help="release version, e.g. 1.0.0")
    args = ap.parse_args()
    cfg = load_config()

    try:
        previous = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0",
             f"v{args.version}~1"], cwd=ROOT, capture_output=True, text=True,
            check=True).stdout.strip()
    except subprocess.CalledProcessError:
        previous = ""

    commits = git_log_since(previous)
    lines = [
        f"# STGR Browser {args.version}",
        "",
        f"Based on **Firefox {cfg['firefox']['upstream_version']}**.",
        "",
        "## Highlights",
        "",
        "- Initial STGR release" if not previous else "- Rebased onto the latest Firefox Stable",
        "- STGR branding",
        "- Privacy-focused defaults (no STGR telemetry)",
        "- uBlock Origin pre-installed",
        "- Gaming Mode",
        "- Dark red/black dojo UI",
        "",
        "## Security",
        "",
        f"- Includes Firefox {cfg['firefox']['upstream_version']} security fixes.",
        "",
        "## Performance",
        "",
        "- Reduced idle background activity",
        "- Lightweight New Tab page",
        "",
        "## What's changed",
        "",
    ]
    if commits:
        lines += [f"- {c}" for c in commits]
    else:
        lines += ["- Initial public release."]
    lines += [
        "",
        "## Known issues",
        "",
        "- See the issue tracker for the current list.",
        "",
        f"*Published {date.today().isoformat()} by STEiGER Dojo.*",
    ]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
