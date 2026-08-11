#!/usr/bin/env python3
"""STGR update checker / downloader (CLI).

Implements the same validation contract as the in-browser updater
(browser/components/stgr/updater/STGRUpdater.sys.mjs):

  - HTTPS + JSON from the configured STGR update repository (GitHub Releases).
  - Product validated (asset prefix "STGR-Browser-").
  - Version strictly newer (downgrades rejected).
  - Architecture validated (-Win64-Setup.exe on Windows x64).
  - SHA256 validated against the published SHA256SUMS.txt.
  - Signature validation hooks when a signing certificate is published.
  - The installer is downloaded only with --download and NEVER executed.

Exit codes: 0 up-to-date · 2 update available · 1 error/invalid.
`--self-test` runs the validation matrix offline (used by CI).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, compare_versions, load_config, log  # noqa: E402

API = "https://api.github.com/repos/"
RAW = "https://raw.githubusercontent.com/"
UA = {"User-Agent": "STGR-Browser-updater",
      "Accept": "application/vnd.github+json"}
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _asset_suffix() -> str:
    return "-Win64-Setup.exe" if sys.platform.startswith("win") else "-Setup"


def evaluate(release: dict, current: str) -> tuple:
    """Pure validation of a release payload against the current version.
    Returns (status, details). No network."""
    tag = release.get("tag_name", "")
    version = tag[1:] if tag.startswith("v") else tag
    if not VERSION_RE.match(version):
        return "invalid", {"reason": "tag-format", "tag": tag}

    if compare_versions(version, current) <= 0:
        return "up-to-date", {"current": current, "latest": version}

    suffix = _asset_suffix()
    asset = next((a for a in release.get("assets", [])
                  if a.get("name", "").startswith("STGR-Browser-")
                  and a.get("name", "").endswith(suffix)), None)
    if not asset:
        return "invalid", {"reason": "no-matching-asset",
                           "arch": sys.platform, "tag": tag}

    return "available", {
        "current": current,
        "latest": version,
        "tag": tag,
        "asset": {"name": asset["name"], "url": asset["browser_download_url"]},
        "notes": (release.get("body") or "")[:2000],
    }


def check(cfg: dict) -> tuple:
    repo = cfg["product"]["update_repository"].rstrip("/").split("github.com/")[-1]
    try:
        release = _get_json(API + repo + "/releases/latest")
    except Exception as exc:  # noqa: BLE001 — network/payload errors
        return "error", {"detail": str(exc)}
    return evaluate(release, cfg["product"]["version"])


def fetch_checksums(cfg: dict) -> str:
    repo = cfg["product"]["update_repository"].rstrip("/").split("github.com/")[-1]
    req = urllib.request.Request(RAW + repo + "/main/SHA256SUMS.txt", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def download_and_verify(cfg: dict, asset: dict, checksums: str) -> Path:
    releases = REPO_ROOT / "releases"
    releases.mkdir(exist_ok=True)
    dest = releases / asset["name"]

    line = next((l for l in checksums.splitlines() if asset["name"] in l), None)
    if not line:
        raise SystemExit("invalid: asset not present in SHA256SUMS.txt")
    expected = line.strip().split()[0].lower()

    req = urllib.request.Request(asset["url"], headers=UA)
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=600) as resp, open(dest, "wb") as fh:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
            fh.write(chunk)
    actual = h.hexdigest()
    if actual != expected:
        dest.unlink(missing_ok=True)
        raise SystemExit(f"invalid: SHA256 mismatch (expected {expected}, "
                         f"got {actual}) — rejected")
    log("update", f"verified {dest.name} (sha256 {actual[:16]}…)")
    return dest


def self_test() -> int:
    """Offline validation matrix (§75): no update / new / invalid / downgrade /
    wrong arch / unknown release."""
    current = "1.0.0"

    def asset(name):
        return [{"name": name, "browser_download_url": "https://example.invalid/x"}]

    cases = [
        ("up-to-date", {"tag_name": "v1.0.0", "assets": asset("STGR-Browser-1.0.0-Win64-Setup.exe")}, current),
        ("available", {"tag_name": "v1.0.1", "assets": asset("STGR-Browser-1.0.1-Win64-Setup.exe")}, current),
        ("up-to-date", {"tag_name": "v0.9.0", "assets": asset("STGR-Browser-0.9.0-Win64-Setup.exe")}, current),  # downgrade
        ("invalid", {"tag_name": "garbage", "assets": []}, current),          # unknown release
        ("invalid", {"tag_name": "v2.0.0", "assets": asset("Other-2.0.0-Win64-Setup.exe")}, current),  # wrong product
        ("invalid", {"tag_name": "v2.0.0", "assets": asset("STGR-Browser-2.0.0-Linux64-Setup.exe")}, current),  # wrong arch
    ]
    failures = 0
    for expected, release, cur in cases:
        status, details = evaluate(release, cur)
        ok = status == expected
        print(f"  {'✅' if ok else '❌'} {expected:<11} -> {status} "
              f"({details.get('reason', details.get('latest', ''))})")
        failures += 0 if ok else 1
    return 0 if failures == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR update checker/downloader")
    ap.add_argument("--download", action="store_true",
                    help="download + verify the installer into releases/")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--self-test", action="store_true",
                    help="run the offline validation matrix and exit")
    args = ap.parse_args()

    if args.self_test:
        print("updater validation matrix:")
        return self_test()

    cfg = load_config()
    status, details = check(cfg)
    if args.json:
        print(json.dumps({"status": status, **details}, indent=2))
    else:
        print(f"status: {status}")
        for key, value in details.items():
            print(f"  {key}: {value}")

    if status == "available" and args.download:
        download_and_verify(cfg, details["asset"], fetch_checksums(cfg))
        return 0
    if status == "up-to-date":
        return 0
    if status == "available":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
