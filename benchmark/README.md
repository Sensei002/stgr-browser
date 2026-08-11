# STGR Benchmark

The benchmark harness (in `scripts/benchmark/benchmark.py`) measures what
matters — startup, idle RAM/CPU, and multi-tab memory — with multiple runs and
median aggregation.

## Metrics

| Metric | Definition |
|---|---|
| `cold_start.seconds` | process spawn → first visible main window |
| `warm_start.seconds` | same, second launch (caches warm) |
| `idle.ram_mb` | process-tree working set, quiet `about:blank` window |
| `idle.cpu_percent` | process-tree CPU over a 20 s idle sample |
| `tabs.{5,10,20}.ram_mb` | process-tree RAM with N background tabs |

## Environment recording

Every result JSON records: STGR version, Firefox version, platform, benchmark
version, timestamp. (Windows version/CPU/GPU are noted in the release notes —
the harness focuses on the metrics CI can gate on.)

## Regression gates (stgr-config.json → benchmark.thresholds)

- startup regression > 15%
- idle memory regression > 20%
- 10-tab memory regression > 20%

`--compare baseline.json` re-measures and fails the build only on real
regressions — never on small benchmark noise (median of `--runs N`).

## Baselines

`baselines/win64.json` is the reference point. The first stable release
establishes the real baseline; until then it is a placeholder. Runs are saved
under `results/` (gitignored).
