#!/usr/bin/env python3
"""Shared helpers for STGR automation scripts.

Stdlib only — the tooling must run anywhere (local Windows, CI) without pip.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "stgr" / "config" / "stgr-config.json"
STATE_DIR = REPO_ROOT / ".stgr"
STATE_FILE = STATE_DIR / "state.json"
FIREFOX_DIR = REPO_ROOT / "firefox"


def load_config() -> dict:
    """Load the central STGR configuration (single source of truth)."""
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def save_state(state: dict) -> None:
    """Persist local state (last-known-good revisions, sync status)."""
    STATE_DIR.mkdir(exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def log(tag: str, msg: str) -> None:
    print(f"[stgr] {tag:<10} {msg}")


def run(
    cmd: list,
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = False,
    timeout: int | None = None,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """Run a command. Raises CalledProcessError on failure when check=True."""
    log("run", " ".join(str(c) for c in cmd))
    try:
        return subprocess.run(
            [str(c) for c in cmd],
            cwd=str(cwd) if cwd else None,
            check=check,
            capture_output=capture,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.CalledProcessError as exc:
        if capture:
            if exc.stdout:
                print(exc.stdout, file=sys.stderr)
            if exc.stderr:
                print(exc.stderr, file=sys.stderr)
        raise


def compare_versions(a: str, b: str) -> int:
    """Return -1/0/1 for a<b/a==b/a>b on dotted numeric versions."""
    pa = [int(x) for x in a.split(".")]
    pb = [int(x) for x in b.split(".")]
    for i in range(max(len(pa), len(pb))):
        da = pa[i] if i < len(pa) else 0
        db = pb[i] if i < len(pb) else 0
        if da != db:
            return -1 if da < db else 1
    return 0
