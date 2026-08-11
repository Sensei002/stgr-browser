#!/usr/bin/env python3
"""Fetch the official, Mozilla-signed uBlock Origin XPI.

Source: gorhill/uBlock GitHub releases (canonical upstream). The XPI is
already signed by Mozilla's add-on signing service, so it installs without
weakening xpinstall.signatures.required.

uBlock Origin is GPL-3.0, © Raymond Hill and contributors — it is bundled
UNMODIFIED with its license/attribution preserved (see
stgr/extensions/ublock-origin/README.md).

Supply-chain tripwire: the first fetch records the SHA256 into
ublock.sha256; later fetches must match it exactly. CI re-runs this to
detect a tampered or unexpected artifact.

Usage:
  fetch         download the pinned version (from stgr-config.json)
  check         verify the local XPI against the recorded hash
  pin --version X.Y.Z   record a new pinned version + hash (review carefully)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, load_config, log  # noqa: E402

DIR = REPO_ROOT / "stgr" / "extensions" / "ublock-origin"
HASH_FILE = DIR / "ublock.sha256"


def asset_name(cfg: dict) -> str:
    return cfg["ublock"]["release_asset_pattern"].format(
        version=cfg["ublock"]["version"])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(cfg: dict) -> Path:
    ver = cfg["ublock"]["version"]
    repo = cfg["ublock"]["source_repository"].rstrip("/")
    url = f"{repo}/releases/download/{ver}/{asset_name(cfg)}"
    dest = DIR / asset_name(cfg)
    DIR.mkdir(parents=True, exist_ok=True)
    log("ublock", f"downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "STGR-Browser"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as fh:
        fh.write(resp.read())
    digest = sha256(dest)
    print(f"downloaded {dest.name}  sha256={digest}")

    if HASH_FILE.exists():
        expected = HASH_FILE.read_text().strip()
        if digest != expected:
            print(f"error: SHA256 mismatch vs {HASH_FILE} — aborting")
            dest.unlink(missing_ok=True)
            return None
    else:
        HASH_FILE.write_text(digest + "\n")
        print(f"recorded new hash -> {HASH_FILE}")
    return dest


def cmd_check(cfg: dict) -> int:
    dest = DIR / asset_name(cfg)
    if not dest.exists():
        print(f"missing {dest}")
        return 1
    if not HASH_FILE.exists():
        print(f"no recorded hash ({HASH_FILE}) — run fetch first")
        return 1
    actual = sha256(dest)
    expected = HASH_FILE.read_text().strip()
    ok = actual == expected
    print(f"{'OK ' if ok else 'MISMATCH'} {dest.name}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="uBlock Origin XPI fetcher")
    ap.add_argument("cmd", choices=["fetch", "check"])
    ap.add_argument("--version", help="pin a different uBlock version")
    args = ap.parse_args()
    cfg = load_config()
    if args.version:
        cfg["ublock"]["version"] = args.version
        cfg_path = REPO_ROOT / "stgr" / "config" / "stgr-config.json"
        cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    if args.cmd == "fetch":
        return 0 if download(cfg) else 1
    return cmd_check(cfg)


if __name__ == "__main__":
    sys.exit(main())
