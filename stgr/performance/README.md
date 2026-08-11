# STGR Performance

Performance is a first-class feature, but it is **measured, not claimed**. See
`docs/performance.md` for the benchmark harness and targets; this directory
holds the memory-profile presets and the design notes.

## Memory profiles (`memory-profiles.json`)

| Profile | Behavior |
|---|---|
| `normal` | Stock Firefox memory behavior |
| `balanced` | Moderate background-tab suspension (600 s idle) |
| `aggressive` | Maximum background reduction: fast suspension (120 s), timer throttling, no background network/preload, animations reduced |

Presets map to the `stgr.memoryProfile.*` prefs in
`stgr/config/preferences/performance.js` and are applied by the Gaming Mode
module (`patches/0004`). Users pick the profile in Settings → Performance.

## Safety rules

- Never unload: active tab, tabs playing audio/video, active downloads,
  WebRTC calls, important web apps.
- Users can pin/protect individual tabs and sites.
- No security process is collapsed, no sandbox disabled, no Windows memory
  hacks. Multi-process architecture stays exactly as upstream.

## Performance claims policy

- No marketing numbers ("50% less RAM!") without controlled benchmarks.
- No benchmark manipulation: the harness measures real cold/warm startup,
  idle RAM/CPU, and N-tab RAM with multiple runs and median aggregation.
- CI gates on regressions (>15% startup, >20% idle memory, >20% 10-tab
  memory) while tolerating benchmark noise.
