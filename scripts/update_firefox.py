#!/usr/bin/env python3
"""STGR Firefox update automation.

Tracks the latest Mozilla Firefox Stable (the `release` branch of the official
git repository, https://github.com/mozilla-firefox/firefox) and keeps STGR
rebased on it.

Commands:
  check   Compare the pinned upstream version against the latest stable.
  sync    Clone/fetch the Firefox source into ./firefox at the pinned release
          tag (e.g. FIREFOX_153_0_RELEASE) — NOT the moving `release` branch
          tip. The STGR patch series is validated against the pinned version
          only; a drifted tip breaks `git apply`.
  update  sync + apply STGR patches (+ build/test when --build/--test) and
          write automation/firefox-<version>/firefox-update-report.md.
  report  Show the last update report summary.

Exit codes: 0 ok (up to date), 2 update available (check mode), 1 error.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    FIREFOX_DIR,
    REPO_ROOT,
    compare_versions,
    load_config,
    load_state,
    log,
    run,
    save_state,
)

API = "https://api.github.com/repos/"
UA = {"User-Agent": "STGR-Browser-update-automation"}


def latest_stable_firefox(cfg: dict) -> dict:
    """Query GitHub for the newest stable Firefox release tag.

    Stable desktop tags look like FIREFOX_153_0_RELEASE / FIREFOX_153_0_3_RELEASE.
    Beta/nightly (b-suffixed) tags are ignored.
    """
    repo = cfg["firefox"]["upstream_repository"].rstrip("/").split("github.com/")[-1]
    req = urllib.request.Request(
        API + repo + "/releases?per_page=100", headers=UA
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        releases = json.load(resp)

    stable = []
    for rel in releases:
        tag = rel.get("tag_name", "")
        # FIREFOX_<maj>_<min>[_<patch>]_RELEASE — no "b" (beta)
        if not (tag.startswith("FIREFOX_") and tag.endswith("_RELEASE")):
            continue
        inner = tag[len("FIREFOX_"):-len("_RELEASE")]
        if "b" in inner or "a" in inner or not inner:
            continue
        parts = inner.split("_")
        if not all(p.isdigit() for p in parts) or len(parts) not in (2, 3):
            continue
        stable.append({
            "tag": tag,
            "version": ".".join(parts),
            "published": rel.get("published_at", ""),
        })
    if not stable:
        raise RuntimeError("no stable Firefox release found via GitHub API")
    return max(stable, key=lambda r: [int(x) for x in r["version"].split(".")])


def sync_source(cfg: dict) -> None:
    """Clone (first time) or update the Firefox source checkout.

    Checks out the PINNED release tag (e.g. FIREFOX_153_0_RELEASE), derived
    from stgr-config.json's upstream_version + release_tag_pattern. Never the
    moving `release` branch tip: dot releases (153.0 -> 153.0.5) drift the
    tree and break `git apply` on the STGR series. This keeps builds
    deterministic and reproducible (spec \u00a773).
    """
    repo = cfg["firefox"]["upstream_repository"]
    tag = cfg["firefox"]["release_tag_pattern"].format(
        version=cfg["firefox"]["upstream_version"])
    if not (FIREFOX_DIR / ".git").exists():
        log("sync", f"cloning {repo} at {tag} (blob:none filter)")
        run(["git", "clone", "--filter=blob:none", "--single-branch",
             "--branch", tag, repo, str(FIREFOX_DIR)])
    else:
        log("sync", f"fetching {tag} into {FIREFOX_DIR}")
        run(["git", "fetch", "--tags", "--force", "origin"], cwd=FIREFOX_DIR)
        run(["git", "checkout", "--force", tag], cwd=FIREFOX_DIR)
        run(["git", "reset", "--hard", tag], cwd=FIREFOX_DIR)
    head = run(["git", "rev-parse", "HEAD"], cwd=FIREFOX_DIR, capture=True)
    log("sync", f"firefox HEAD: {head.stdout.strip()}")


class PatchConflict(Exception):
    """Raised when the STGR patch series cannot be applied cleanly."""

    def __init__(self, results: list):
        super().__init__("STGR patch conflicts — see firefox-update-report.md")
        self.results = results


def apply_stgr_patches() -> list:
    from apply_patches import check_series
    results = check_series(apply=True)
    failed = [r for r in results if not r["ok"]]
    if failed:
        raise PatchConflict(results)
    return results


def write_report(cfg: dict, latest: dict, results: dict) -> Path:
    """Write automation/firefox-<version>/firefox-update-report.md"""
    out_dir = REPO_ROOT / "automation" / f"firefox-{latest['version']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / "firefox-update-report.md"
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        f"# Firefox update report — {latest['version']}",
        "",
        f"- Generated: {now}",
        f"- Old upstream: {cfg['firefox']['upstream_version']}",
        f"- New upstream: {latest['version']}",
        f"- Release tag: {latest['tag']}",
        f"- STGR version: {cfg['product']['version']}",
        "",
        "## Patch application",
    ]
    for p in results.get("patches", []):
        status = "✅" if p.get("ok") else "❌ FAILED"
        lines.append(f"- {status} {p['name']}")
    failed = [p for p in results.get("patches", []) if not p.get("ok")]
    if failed:
        lines += ["", "## Files requiring manual review"]
        for p in failed:
            lines += [f"- {p['name']} — {p.get('error', 'unknown')}"]
        lines += ["", "> **Do not publish a release until conflicts are resolved.**"]
    if results.get("build"):
        lines += ["", f"## Build: {results['build']}"]
    if results.get("tests"):
        lines += ["", f"## Tests: {results['tests']}"]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def cmd_check(cfg: dict) -> int:
    latest = latest_stable_firefox(cfg)
    pinned = cfg["firefox"]["upstream_version"]
    log("check", f"pinned upstream {pinned}, latest stable {latest['version']} "
                 f"({latest['published'][:10]})")
    if compare_versions(latest["version"], pinned) > 0:
        print(f"UPDATE AVAILABLE: {pinned} -> {latest['version']}")
        return 2
    print("UP TO DATE")
    return 0


def cmd_sync(cfg: dict) -> int:
    sync_source(cfg)
    return 0


def cmd_update(cfg: dict, args) -> int:
    latest = latest_stable_firefox(cfg)
    pinned = cfg["firefox"]["upstream_version"]
    state = load_state()
    if compare_versions(latest["version"], pinned) <= 0 and not args.force:
        log("update", f"already on {pinned} (latest {latest['version']})")
        return 0

    log("update", f"rebasing onto Firefox {latest['version']}")
    sync_source(cfg)

    # Remember the previous known-good revision for rollback.
    if not state.get("LAST_KNOWN_GOOD_FIREFOX"):
        state["LAST_KNOWN_GOOD_FIREFOX"] = pinned
    if not state.get("LAST_KNOWN_GOOD_STGR"):
        state["LAST_KNOWN_GOOD_STGR"] = cfg["product"]["version"]

    results = {"patches": []}
    try:
        results["patches"] = apply_stgr_patches()
    except PatchConflict as exc:
        results["patches"] = exc.results
        write_report(cfg, latest, results)
        print("Patch conflicts detected — see firefox-update-report.md. "
              "Rollback: checkout LAST_KNOWN_GOOD revision.")
        return 1

    if args.build:
        from build_stgr import build
        results["build"] = build(cfg)
    if args.test:
        from smoke_test import run_smoke_test
        results["tests"] = run_smoke_test(cfg)

    report = write_report(cfg, latest, results)

    state["FIREFOX_UPSTREAM_VERSION"] = latest["version"]
    state["FIREFOX_REVISION"] = run(["git", "rev-parse", "HEAD"],
                                    cwd=FIREFOX_DIR, capture=True).stdout.strip()
    save_state(state)

    cfg["firefox"]["upstream_version"] = latest["version"]
    cfg_path = REPO_ROOT / "stgr" / "config" / "stgr-config.json"
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    print(f"Update report: {report}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR Firefox update automation")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("sync")
    p_update = sub.add_parser("update")
    p_update.add_argument("--build", action="store_true",
                          help="run the STGR build after patching")
    p_update.add_argument("--test", action="store_true",
                          help="run the browser smoke test after building")
    p_update.add_argument("--force", action="store_true",
                          help="rebase even if pinned version is current")
    sub.add_parser("report")

    args = ap.parse_args()
    cfg = load_config()
    if args.cmd == "check":
        return cmd_check(cfg)
    if args.cmd == "sync":
        return cmd_sync(cfg)
    if args.cmd == "update":
        return cmd_update(cfg, args)
    if args.cmd == "report":
        state = load_state()
        print(json.dumps(state, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
