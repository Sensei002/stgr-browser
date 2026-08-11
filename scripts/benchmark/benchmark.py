#!/usr/bin/env python3
"""STGR performance benchmark harness (§60–61).

Measures on Windows x64:
  cold_start   — time from process spawn to first visible main window
  warm_start   — same for a second launch (page/disk caches warm)
  idle         — process-tree RAM + CPU over a quiet window (about:blank)
  tabs_5/10/20 — process-tree RAM with N background tabs

Results are written to benchmark/results/benchmark-<ts>.json. `--compare`
applies the configurable regression thresholds from stgr-config.json
(startup >15%, idle memory >20%, 10-tab memory >20%) and fails the build on a
real regression — never on benchmark noise (use `--runs N`, compare medians).

Usage:
  python scripts/benchmark/benchmark.py --binary <firefox.exe> [--runs 3]
  python scripts/benchmark/benchmark.py --compare benchmark/baselines/win64-v1.0.0.json
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import REPO_ROOT, load_config, log  # noqa: E402
from smoke_test import find_binary, kill_tree, launch  # noqa: E402
from _win import find_window_for_pid, tree_cpu_delta_seconds, tree_memory_bytes  # noqa: E402

RESULTS_DIR = REPO_ROOT / "benchmark" / "results"
MB = 1024 * 1024


def startup(binary: Path, profile: Path, warm: bool) -> dict:
    proc = launch(binary, profile, ["about:blank"])
    t0 = time.perf_counter()
    win = find_window_for_pid(proc.pid, title_substr="STGR", timeout=90)
    elapsed = time.perf_counter() - t0
    kill_tree(proc)
    return {"seconds": round(elapsed, 3), "window_found": win is not None}


def idle(binary: Path, profile: Path, duration: float = 20.0) -> dict:
    proc = launch(binary, profile, ["about:blank"])
    find_window_for_pid(proc.pid, title_substr="STGR", timeout=90)
    time.sleep(6)  # settle after startup churn
    ram = tree_memory_bytes(proc.pid)
    cpu = tree_cpu_delta_seconds(proc.pid, duration)
    kill_tree(proc)
    return {
        "ram_mb": round((ram or 0) / MB, 1),
        "cpu_seconds": round(cpu, 2),
        "cpu_percent": round(cpu / duration * 100, 2),
    }


def tabs(binary: Path, profile: Path, count: int, url: str) -> dict:
    proc = launch(binary, profile, [url] * count)
    find_window_for_pid(proc.pid, title_substr="STGR", timeout=120)
    time.sleep(10)  # let the tabs settle
    ram = tree_memory_bytes(proc.pid)
    kill_tree(proc)
    return {"tabs": count, "ram_mb": round((ram or 0) / MB, 1)}


def run_all(binary: Path, runs: int, url: str) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="stgr-bench-"))
    profile = tmp / "profile"
    profile.mkdir(parents=True)
    (profile / "user.js").write_text("", encoding="utf-8")

    runs_data = {}
    for r in range(runs):
        tag = f"run{r + 1}"
        cold = startup(binary, profile, warm=False)
        warm = startup(binary, profile, warm=True)
        idle_r = idle(binary, profile)
        tabs_r = {n: tabs(binary, profile, n, url) for n in (5, 10, 20)}
        runs_data[tag] = {"cold_start": cold, "warm_start": warm,
                          "idle": idle_r, "tabs": tabs_r}
        log("bench", f"{tag}: cold={cold['seconds']}s "
                     f"idle_ram={idle_r['ram_mb']}MB "
                     f"tabs10={tabs_r[10]['ram_mb']}MB")
    return aggregate(runs_data)


def aggregate(runs: dict) -> dict:
    """Median across runs for every metric."""
    keys = ["cold_start.seconds", "warm_start.seconds", "idle.ram_mb",
            "idle.cpu_percent", "tabs.5.ram_mb", "tabs.10.ram_mb",
            "tabs.20.ram_mb"]

    def get(run, key):
        node = run
        for part in key.split("."):
            node = node[part]
        return node

    count = len(runs)
    out = {}
    for key in keys:
        values = sorted(get(runs[f"run{i + 1}"], key) for i in range(count))
        out[key] = values[count // 2]
    return out


def compare(metrics: dict, baseline: dict, cfg: dict) -> list:
    """Return [(metric, value, base, change_pct)] for regressions."""
    thresholds = cfg["benchmark"]["thresholds"]
    mapping = {
        "cold_start.seconds": "startup",
        "warm_start.seconds": "startup",
        "idle.ram_mb": "idle_memory",
        "tabs.10.ram_mb": "ten_tab_memory",
    }
    failures = []
    for metric, value in metrics.items():
        rule = mapping.get(metric)
        if not rule:
            continue
        base = baseline.get(metric)
        if base is None or base == 0:
            continue
        change = (value - base) / base * 100
        limit = thresholds.get(rule + "_regression_pct", 20)
        status = "ok" if change <= limit else "REGRESSION"
        log("compare", f"{metric}: {value} vs {base} ({change:+.1f}%) "
                       f"[limit +{limit}%] {status}")
        if change > limit:
            failures.append((metric, value, base, round(change, 1)))
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR benchmark harness")
    ap.add_argument("--binary", type=Path, help="path to firefox.exe")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--url", default="about:blank",
                    help="tab workload URL (about:blank for offline CI)")
    ap.add_argument("--compare", type=Path,
                    help="baseline JSON; measures current build and compares")
    args = ap.parse_args()
    cfg = load_config()
    binary = args.binary or find_binary()

    if args.compare:
        baseline = json.loads(args.compare.read_text(encoding="utf-8"))
        baseline_metrics = baseline.get("metrics", baseline)
        log("compare", f"measuring current build against {args.compare.name} "
                       f"({args.runs} runs)")
        metrics = run_all(binary, args.runs, args.url)
        failures = compare(metrics, baseline_metrics, cfg)
        if failures:
            print("PERFORMANCE REGRESSION DETECTED")
            for metric, value, base, change in failures:
                print(f"  ❌ {metric}: {value} vs {base} ({change:+.1f}%)")
            return 1
        print("NO REGRESSION vs baseline")
        return 0

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = RESULTS_DIR / f"benchmark-{ts}.json"
    payload = {
        "stgr_version": cfg["product"]["version"],
        "firefox_version": cfg["firefox"]["upstream_version"],
        "platform": "windows-x64",
        "benchmark_version": "1.0.0",
        "runs": args.runs,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metrics": run_all(binary, args.runs, args.url),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"benchmark written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
