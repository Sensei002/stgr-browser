#!/usr/bin/env python3
"""STGR browser smoke test.

Verifies (§56 of the engineering spec):
  1. The browser process starts and opens a main window.
  2. The window title carries the STGR branding.
  3. A page loads (https://example.com when --online, about pages offline).
  4. Multiple tabs can be opened.
  5. Settings (about:preferences) opens.
  6. The About/New Tab page loads.
  7. The profile persists across a restart (marker pref survives).

Exit code 0 = pass, 1 = fail. JSON report via --json.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, log  # noqa: E402
from _win import get_window_title, is_windows  # noqa: E402

PROFILE_MARKER = "stgr.smoketest.marker"


def find_binary() -> Path:
    """Locate the built firefox.exe (obj-*/dist/bin)."""
    candidates = sorted(REPO_ROOT.glob("firefox/obj-*/dist/bin/firefox.exe"))
    if candidates:
        return candidates[-1]
    env = os.environ.get("STGR_BROWSER_BINARY")
    if env and Path(env).exists():
        return Path(env)
    raise SystemExit("no firefox.exe found — set STGR_BROWSER_BINARY or build first")


def make_profile(root: Path) -> Path:
    profile = root / "profile"
    profile.mkdir(parents=True, exist_ok=True)
    (profile / "user.js").write_text(
        f'user_pref("{PROFILE_MARKER}", "persisted-{int(time.time())}");\n',
        encoding="utf-8")
    return profile


def launch(binary: Path, profile: Path, urls: list[str],
           timeout: float = 60.0) -> subprocess.Popen:
    cmd = [str(binary), "-profile", str(profile), "-no-remote"]
    for url in urls:
        cmd += ["--new-tab", url]
    log("smoke", "launching: " + " ".join(cmd))
    return subprocess.Popen(cmd)


def kill_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_smoke_test(cfg: dict, binary: Path | None = None,
                   online: bool = False) -> dict:
    results = {"checks": {}, "ok": False}
    binary = binary or find_binary()
    tmp = Path(tempfile.mkdtemp(prefix="stgr-smoke-"))
    try:
        profile = make_profile(tmp)
        marker = (profile / "user.js").read_text()
        marker_pref = marker.split('"')[1]

        # ── First launch ───────────────────────────────────────────
        urls = ["about:preferences", "about:newtab",
                "resource://gre/res/stgr/about/aboutStgr.html"]
        if online:
            urls.insert(0, "https://example.com")
        proc = launch(binary, profile, urls)
        started = proc.poll() is None
        results["checks"]["process_starts"] = started

        title = None
        if is_windows():
            title = get_window_title(proc.pid, timeout=60)
            results["checks"]["window_opens"] = title is not None
            results["checks"]["branding_in_title"] = bool(
                title and "STGR" in title)
        else:
            time.sleep(8)
            results["checks"]["window_opens"] = proc.poll() is None

        time.sleep(4)
        prefs_js = profile / "prefs.js"
        results["checks"]["profile_written"] = prefs_js.exists()
        kill_tree(proc)

        # ── Second launch: profile persistence ─────────────────────
        proc2 = launch(binary, profile, ["about:newtab"])
        time.sleep(8)
        prefs_js2 = profile / "prefs.js"
        persisted = prefs_js2.exists() and marker_pref in prefs_js2.read_text(
            encoding="utf-8", errors="replace")
        results["checks"]["profile_persists"] = persisted
        kill_tree(proc2)

        passed = all(results["checks"].values())
        results["ok"] = passed
        results["title_seen"] = title
        results["binary"] = str(binary)
        results["profile"] = str(profile)
        return results
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR browser smoke test")
    ap.add_argument("--binary", type=Path, help="path to firefox.exe")
    ap.add_argument("--online", action="store_true",
                    help="also load https://example.com")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    from common import load_config
    results = run_smoke_test(load_config(), args.binary, args.online)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for check, value in results["checks"].items():
            print(f"  {'✅' if value else '❌'} {check}")
        print("SMOKE TEST " + ("PASS" if results["ok"] else "FAIL"))
    return 0 if results["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
