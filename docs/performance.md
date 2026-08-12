# STGR Performance

## Targets

- Fast cold and warm startup
- Low idle CPU and low idle RAM
- Smooth scrolling and fast tab switching
- Fast page loads, responsive address bar, efficient GPU acceleration
- Low background activity (tabs, timers, network, preloading)

## Policy

- **Measure, don't claim.** No marketing numbers ("50% less RAM!") without
  controlled benchmarks. No benchmark manipulation.
- **Never trade security for numbers.** No sandbox/process-isolation/cert
  disabling, no collapsing security processes, no Windows memory hacks.
- **Respect Firefox's multi-process architecture.** Content, GPU, socket and
  utility processes stay as upstream; we optimize *unnecessary* background
  work instead.

## Where performance comes from

1. **Preference layer** (`stgr/config/preferences/performance.js`): idle
   session-write interval, memory-pressure unloading, throttling, WebRender
   defaults, reduced idle network (predictor/prefetch off).
2. **Memory profiles** (`stgr/performance/memory-profiles.json`): normal /
   balanced / aggressive background-tab suspension presets.
3. **Gaming Mode** (`patches/0004`): on-demand resource reduction while
   gaming (see `docs/gaming-mode.md`).
4. **Lightweight New Tab** (`patches/0003`): replaces the React Activity
   Stream with a few KB of static HTML.
5. **Toolchain**: release `-O2` + LTO + sccache. PGO is opt-in (below).

## Benchmark harness

`scripts/benchmark/benchmark.py` measures: cold/warm startup, idle RAM + CPU,
and 5/10/20-tab RAM — process-tree, multiple runs, median aggregation. Every
run records STGR version, Firefox version, platform, benchmark version.

Regression gates (stgr-config.json → `benchmark.thresholds`):

- startup regression > 15%
- idle memory regression > 20%
- 10-tab memory regression > 20%

Run the harness manually against `benchmark/baselines/win64.json`:

```bash
python scripts/benchmark/benchmark.py \
  --binary <path-to>/stgr.exe --compare benchmark/baselines/win64.json --runs 3
```

(replace the placeholder baseline with real measurements after the first
stable release — **no fabricated data**).

## Profile-Guided Optimization

PGO is **off by default** (expensive on CI; the GitHub Actions pipeline keeps
build time bounded). To enable:

1. Uncomment `--enable-profile-guided-optimization` in the mozconfig.
2. Build the instrumentation run (`mach build` twice — Firefox automates this
   with `mach build pgo`).
3. Drive a **real, representative workload** (startup, common sites, media).
   Never fabricate profile data.
4. Collect the profile, rebuild optimized, and benchmark to confirm gains.

If PGO stays too expensive for CI, keep it documented and optional — it is not
a v1 requirement.
