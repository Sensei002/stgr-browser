#!/usr/bin/env python3
"""STGR privacy network test (§57).

Launches the browser pointed at a local capturing proxy and records every host
the browser tries to contact (CONNECT for HTTPS, absolute-URI GET for HTTP).
The host set is compared against an allowlist of legitimate security/browser
functionality (update checks, extension services, safe browsing, remote
settings) plus hosts explicitly visited by the test.

The test FAILS if any unexpected host is contacted — especially any telemetry
or data-reporting endpoint. It identifies the *source* (which URL/request
triggered it) rather than merely blocking traffic.

Note: the proxy records connection intent (hostnames), not content. HTTPS
payloads are not decrypted or inspected.

Exit code 0 = no unexpected outbound hosts, 1 = violations found.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, load_config, log  # noqa: E402
from smoke_test import find_binary, kill_tree, launch  # noqa: E402

SEEN: list[dict] = []
SEEN_LOCK = threading.Lock()


class _Handler(BaseHTTPRequestHandler):
    def _record(self, kind: str, host: str, path: str) -> None:
        with SEEN_LOCK:
            SEEN.append({"kind": kind, "host": host.lower(), "path": path})
        self.send_response(502)  # do not tunnel; we only observe intent
        self.end_headers()

    def do_CONNECT(self):  # HTTPS: host:port
        host = self.path.split(":")[0]
        self._record("https", host, "")
        self.wfile.write(b"HTTP/1.1 502 Blocked by STGR privacy test\r\n\r\n")

    def do_GET(self):  # HTTP absolute URI
        parts = self.path.split("/", 3)
        self._record("http", parts[2] if len(parts) > 2 else self.path,
                     self.path)

    def log_message(self, *args):  # keep output quiet
        pass


def run_privacy_test(cfg: dict, binary: Path | None = None,
                     duration: int = 25) -> dict:
    global SEEN
    SEEN = []
    binary = binary or find_binary()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    tmp = Path(tempfile.mkdtemp(prefix="stgr-privacy-"))
    try:
        profile = tmp / "profile"
        profile.mkdir(parents=True)
        (profile / "user.js").write_text(
            "user_pref(\"network.proxy.type\", 1);\n"
            f"user_pref(\"network.proxy.http\", \"127.0.0.1\");\n"
            f"user_pref(\"network.proxy.http_port\", {port});\n"
            f"user_pref(\"network.proxy.ssl\", \"127.0.0.1\");\n"
            f"user_pref(\"network.proxy.ssl_port\", {port});\n"
            "user_pref(\"network.proxy.no_proxies_on\", \"\");\n"
            "user_pref(\"network.proxy.share_proxy_settings\", true);\n",
            encoding="utf-8")

        proc = launch(binary, profile,
                      ["about:newtab", "https://example.com"])
        time.sleep(duration)
        kill_tree(proc)
    finally:
        server.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    allowlist = {h.lower() for h in cfg["privacy"]["allowed_background_hosts"]}
    allowlist |= {"example.com", "localhost", "127.0.0.1"}
    unexpected = [s for s in SEEN if s["host"] not in allowlist
                  and not s["host"].endswith("mozilla.org")]

    forbidden_markers = ["telemetry.mozilla.org", "incoming.telemetry",
                         "analytics", "pioneer", "normandy"]
    violations = [s for s in SEEN if any(m in s["host"] for m in forbidden_markers)]

    return {
        "ok": not unexpected and not violations,
        "contacts": SEEN,
        "unexpected": unexpected,
        "violations": violations,
        "allowlist": sorted(allowlist),
        "note": "proxy observes connection intent only; HTTPS payloads are not decrypted",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR privacy network test")
    ap.add_argument("--binary", type=Path)
    ap.add_argument("--duration", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    results = run_privacy_test(cfg, args.binary, args.duration)
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"hosts contacted ({len(results['contacts'])}):")
        for c in results["contacts"]:
            print(f"  {c['kind']:<5} {c['host']}")
        if results["unexpected"]:
            print("\nUNEXPECTED HOSTS:")
            for u in results["unexpected"]:
                print(f"  ❌ {u['kind']} {u['host']} (path: {u['path'][:80]})")
        if results["violations"]:
            print("\nTELEMETRY-LIKE CONTACTS:")
            for v in results["violations"]:
                print(f"  ❌ {v['host']}")
    print("PRIVACY TEST " + ("PASS" if results["ok"] else "FAIL"))
    return 0 if results["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
