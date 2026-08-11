#!/usr/bin/env python3
"""STGR patch series tooling.

Applies patches/ (in `series` order) onto the Firefox source checkout at
./firefox using `git apply`. Conflict policy: STOP on first failure and report
— never force a patch. A failed series is a release-blocking condition.

Commands:
  check   Dry-run: verify every patch applies cleanly (exit 0) or report failures.
  apply   Apply the series in order; stop at the first conflict.
  status  Show which patches are currently applied.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FIREFOX_DIR, REPO_ROOT, log, run  # noqa: E402

SERIES = REPO_ROOT / "patches" / "series"


def series_list() -> list[str]:
    """Patch file paths (repo-relative) in order, ignoring comments/blank lines."""
    patches = []
    for line in SERIES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patches.append(line)
    return patches


def _git(cmd: list, patch: str, check: bool = False):
    # Always feed git apply an LF-normalized patch via stdin (git apply -).
    #   - The Firefox tree is ALWAYS LF: upstream .gitattributes forces
    #     `* -text` (no line-ending normalization) on every checkout.
    #   - git apply only matches a CRLF patch against a CRLF tree, so a patch
    #     file checked out CRLF would fail against the LF Firefox tree
    #     ("patch does not apply"). LF patches apply cleanly to BOTH LF and
    #     CRLF trees (verified via an apply matrix). This stdin normalization
    #     is the primary guarantee; the repo .gitattributes (eol=lf for *.patch)
    #     is defense-in-depth for anything that applies the files by path.
    #   - encoding="utf-8" so the non-ASCII patch content (e.g. \u9053\u5834 in the
    #     new-tab patch) survives even on a cp1252 Windows console without
    #     PYTHONUTF8.
    #   - Deliberately NO `--recount`: it mis-parses the known-good hunks in
    #     this series (verified: 0004 fails with --recount, passes without).
    data = (REPO_ROOT / patch).read_text(encoding="utf-8").replace("\r\n", "\n")
    return run(["git", "apply", *cmd, "-"], cwd=FIREFOX_DIR,
               check=check, capture=True, input=data, encoding="utf-8")


def check_series(apply: bool) -> list[dict]:
    """Run git apply --check (or apply) per patch; returns result records.

    Conflict policy: a patch that no longer applies cleanly (e.g. after a
    Firefox release) fails loudly and stops the series — never force it.
    Hunk counts in this series are machine-verified; see patches/README.md.
    """
    results = []
    for patch in series_list():
        base = []
        if not apply:
            base.append("--check")
        res = _git(base, patch, check=False)
        ok = res.returncode == 0
        results.append({
            "name": patch,
            "ok": ok,
            "error": (res.stderr or res.stdout or "").strip()[:300] if not ok else "",
        })
        if ok:
            log("patch", f"✅ {patch}")
        else:
            log("patch", f"❌ {patch}")
            if apply:
                log("patch", "stopping: do not force-fix conflicting patches")
                break
    return results


def print_report(results: list[dict]) -> None:
    for r in results:
        mark = "ok" if r["ok"] else "FAILED"
        print(f"  [{mark:>6}] {r['name']}")
        if r["error"]:
            print(f"          {r['error']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR patch series tooling")
    ap.add_argument("cmd", choices=["check", "apply", "status"])
    args = ap.parse_args()

    if not (FIREFOX_DIR / ".git").exists():
        print("error: ./firefox is not a git checkout. Run: "
              "python scripts/update_firefox.py sync", file=sys.stderr)
        return 1

    if args.cmd == "status":
        for patch in series_list():
            res = _git(["--reverse", "--check"], patch, check=False)
            applied = res.returncode == 0
            log("status", f"{'applied  ' if applied else 'not applied'} {patch}")
        return 0

    results = check_series(apply=(args.cmd == "apply"))
    print()
    print_report(results)
    failed = [r for r in results if not r["ok"]]
    if failed:
        print()
        print("RELEASE BLOCKING: patches failed to apply. See "
              "patches/README.md for the conflict policy.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
