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
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FIREFOX_DIR, REPO_ROOT, log, run  # noqa: E402

SERIES = REPO_ROOT / "patches" / "series"
PATCH_MARKER = FIREFOX_DIR / ".stgr-patched"


def _clear_patch_marker() -> None:
    """Invalidate the marker before a new patch transaction starts."""
    PATCH_MARKER.unlink(missing_ok=True)


def _series_digest(patches: list[str] | None = None) -> str:
    """Hash the ordered patch list and exact normalized patch contents."""
    digest = hashlib.sha256()
    for patch in patches if patches is not None else series_list():
        digest.update(patch.encode("utf-8"))
        digest.update(b"\x00")
        digest.update((REPO_ROOT / patch).read_bytes().replace(b"\r\n", b"\n"))
        digest.update(b"\x00")
    return digest.hexdigest()


def _patch_paths(patches: list[str]) -> list[str]:
    """Return all repository-relative files touched by an ordered series."""
    paths = set()
    for patch in patches:
        for line in (REPO_ROOT / patch).read_text(encoding="utf-8").splitlines():
            if not (line.startswith("--- ") or line.startswith("+++ ")):
                continue
            path = line[4:].split("\\t", 1)[0]
            if path == "/dev/null":
                continue
            if path.startswith("a/") or path.startswith("b/"):
                path = path[2:]
            paths.add(path)
    return sorted(paths)


def _file_hashes(patches: list[str] | None = None) -> dict[str, str | None]:
    """Hash the final bytes of every file touched by the patch series."""
    hashes = {}
    for rel in _patch_paths(patches if patches is not None else series_list()):
        path = FIREFOX_DIR / rel
        if not path.is_file():
            hashes[rel] = None
            continue
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _firefox_revision() -> str | None:
    """Return the upstream Firefox HEAD, or None if the checkout is invalid."""
    try:
        result = run(["git", "rev-parse", "HEAD"], cwd=FIREFOX_DIR,
                     check=False, capture=True)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _write_patch_marker(patches: list[str]) -> None:
    """Record the exact upstream tree and patch series that were applied."""
    revision = _firefox_revision()
    if revision is None:
        raise RuntimeError("cannot write patch marker: Firefox HEAD is unavailable")
    try:
        PATCH_MARKER.write_text(
            json.dumps({
                "firefox_revision": revision,
                "patch_series_sha256": _series_digest(patches),
                "file_hashes": _file_hashes(patches),
            }, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeError(f"cannot write patch marker: {exc}") from exc


def marker_is_valid() -> bool:
    """Return whether metadata and every patch still match the worktree."""
    try:
        marker = json.loads(PATCH_MARKER.read_text(encoding="utf-8"))
        if (marker.get("firefox_revision") != _firefox_revision()
                or marker.get("patch_series_sha256") != _series_digest()
                or marker.get("file_hashes") != _file_hashes()):
            return False
        return True
    except (FileNotFoundError, OSError, json.JSONDecodeError, RuntimeError):
        return False


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
    # Apply an LF-normalized patch from a temporary FILE, never via stdin:
    # subprocess text-mode stdin translates '\n' to '\r\n' on Windows
    # (os.linesep), so 'git apply -' would receive a CRLF patch. git apply
    # only matches a CRLF patch against a CRLF tree, and the Firefox tree is
    # LF on CI (runner autocrlf differs from local machines) — a CRLF patch
    # fails with "patch does not apply" (reproduced). An LF patch file
    # applies cleanly to both LF and CRLF trees (verified via an apply
    # matrix). Writing exact bytes to a temp file avoids all text-mode
    # translation on every platform; byte-level normalization also keeps
    # non-ASCII patch content (e.g. the new-tab \u9053\u5834) intact.
    # Deliberately NO `--recount`: it mis-parses the known-good hunks in
    # this series (verified: 0004 fails with --recount, passes without).
    data = (REPO_ROOT / patch).read_bytes().replace(b"\r\n", b"\n")
    fd, tmp = tempfile.mkstemp(suffix=".patch")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        return run(["git", "apply", *cmd, tmp], cwd=FIREFOX_DIR,
                   check=check, capture=True)
    finally:
        os.unlink(tmp)


def check_series(apply: bool) -> list[dict]:
    """Run git apply --check (or apply) per patch; returns result records.

    Conflict policy: a patch that no longer applies cleanly (e.g. after a
    Firefox release) fails loudly and stops the series — never force it.
    Hunk counts in this series are machine-verified; see patches/README.md.
    """
    results = []
    patches = series_list()
    if apply:
        # A sync/reset may have changed the Firefox tree, so never trust a
        # marker from an earlier checkout. The marker is recreated only after
        # every patch in this run succeeds.
        _clear_patch_marker()

    for patch in patches:
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

    if apply and len(results) == len(patches) and all(r["ok"] for r in results):
        _write_patch_marker(patches)
        log("patch", f"marker written: {PATCH_MARKER}")
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
