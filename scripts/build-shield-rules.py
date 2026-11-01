#!/usr/bin/env python3
"""
Compile hosts-style blocklists into Manifest V3 declarativeNetRequest rulesets.

Why compile at build time instead of using an ABP engine at runtime:
  * DNR rules are evaluated inside the network stack, before a socket opens.
    An extension-level blocker (uBO style content filtering) has to run JS per
    request; that costs memory and CPU, which is the exact opposite of what a
    low-RAM browser needs.
  * No filter list is downloaded at runtime, so blocking works offline and no
    request metadata ever leaves the machine.

Output: extensions/stgr-shield/rules/ruleset-<n>.json  (deterministic, sorted)
Run:    python scripts/build-shield-rules.py [--offline]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHIELD = ROOT / "extensions" / "stgr-shield"
RULES_DIR = SHIELD / "rules"
SOURCES = ROOT / "config" / "blocklists" / "sources.json"

HOST_LINE = re.compile(r"^\s*(?:0\.0\.0\.0|127\.0\.0\.1|::1)?\s*([a-z0-9][a-z0-9._-]*)\s*(?:#.*)?$", re.I)

# Hosts that must never be blocked: they are infrastructure, not advertising.
# Blocking any of these breaks the browser or the OS in ways users cannot debug.
NEVER_BLOCK = {
    "localhost", "localhost.localdomain", "local", "broadcasthost",
    "ip6-localhost", "ip6-loopback", "ip6-allnodes", "ip6-allrouters",
    "0.0.0.0", "127.0.0.1", "::1",
}


def load_sources() -> dict:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def read_hosts_file(path: Path) -> set[str]:
    domains: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        match = HOST_LINE.match(line)
        if not match:
            continue
        host = match.group(1).lower().strip(".")
        if host in NEVER_BLOCK or "." not in host:
            continue
        domains.add(host)
    return domains


def fetch(url: str, timeout: int = 25) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "STGR-Browser-Build/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 - build must survive a flaky mirror
        print(f"  ! skipped {url.split('/')[2]}: {exc}", file=sys.stderr)
        return None


def collect(offline: bool) -> set[str]:
    spec = load_sources()
    domains: set[str] = set()

    for source in spec["sources"]:
        if not source.get("enabled"):
            continue

        before = len(domains)
        if "path" in source:
            path = ROOT / source["path"]
            if path.exists():
                domains |= read_hosts_file(path)
        elif "url" in source and not offline:
            body = fetch(source["url"])
            if body:
                tmp = ROOT / ".cache" / f"{source['id']}.txt"
                tmp.parent.mkdir(exist_ok=True)
                tmp.write_text(body, encoding="utf-8")
                domains |= read_hosts_file(tmp)
        print(f"  {source['id']}: +{len(domains) - before}")

    return domains


def to_rules(domains: set[str], start_id: int = 1) -> list[dict]:
    rules = []
    for index, host in enumerate(sorted(domains), start=start_id):
        rules.append(
            {
                "id": index,
                "priority": 1,
                "action": {"type": "block"},
                # '||host^' anchors on the domain boundary: matches the domain and
                # any subdomain, and nothing that merely contains the string.
                "condition": {
                    "urlFilter": f"||{host}^",
                    "isUrlFilterCaseSensitive": False,
                },
            }
        )
    return rules


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="use only local lists")
    args = parser.parse_args()

    spec = load_sources()
    per_ruleset = int(spec.get("maxRulesPerRuleset", 25000))
    max_total = int(spec.get("maxTotalRules", 75000))

    print("collecting blocklists")
    domains = collect(args.offline)
    if not domains:
        print("error: no domains collected", file=sys.stderr)
        return 1

    ordered = sorted(domains)[:max_total]
    dropped = len(domains) - len(ordered)

    RULES_DIR.mkdir(parents=True, exist_ok=True)
    for stale in RULES_DIR.glob("ruleset-*.json"):
        stale.unlink()

    chunks = [ordered[i : i + per_ruleset] for i in range(0, len(ordered), per_ruleset)]
    manifest_path = SHIELD / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    resources = []
    for index, chunk in enumerate(chunks):
        rules = to_rules(set(chunk), start_id=1)
        out = RULES_DIR / f"ruleset-{index}.json"
        out.write_text(json.dumps(rules, separators=(",", ":")), encoding="utf-8")
        resources.append(
            {"id": f"stgr-{index}", "enabled": True, "path": f"rules/ruleset-{index}.json"}
        )
        print(f"  ruleset-{index}.json: {len(rules)} rules, {out.stat().st_size // 1024} KiB")

    manifest["declarative_net_request"]["rule_resources"] = resources
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if dropped:
        print(f"warning: {dropped} domains dropped at the {max_total} rule ceiling", file=sys.stderr)
    print(f"done: {len(ordered)} domains across {len(chunks)} ruleset(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
