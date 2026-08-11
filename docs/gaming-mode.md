# STGR Gaming Mode

Gaming Mode is **browser resource management while you game** — not a magical
FPS booster, and never anything that touches your games.

## What it does (when enabled)

- Suspends **background tabs** where safe (idle tabs without audio/video/
  downloads/WebRTC/active content)
- Reduces background **timers** and session-write frequency
- Reduces background **network** and preloading
- Reduces **browser UI animation**
- Prioritizes **active tab** responsiveness
- Applied via `patches/0004` (`STGRGamingMode.sys.mjs`) + the performance
  pref block; toggled by `stgr.gamingMode.enabled` (`off | on | automatic`)

## What it never does

- Terminates Steam, Discord, or game processes
- Modifies game memory or injects code into games
- Touches anti-cheat, GPU drivers, or overclocks hardware
- Disables Windows security or antivirus
- Interferes with other applications

## Protection rules

Never unload: the active tab, tabs playing **audio/video**, active
**downloads**, **WebRTC calls**, or important web apps. Users can pin/protect
individual tabs and sites.

## Controls

- Toolbar: Gaming Mode **OFF/ON** toggle with a subtle indicator
  (`#stgr-gaming-indicator`)
- Settings → Performance → Gaming Mode: `OFF | ON | AUTOMATIC`
- `AUTOMATIC` (when implemented later) uses a **passive, non-invasive
  heuristic** — no invasive system monitoring

## Memory profiles

Settings → Performance also offers `NORMAL | BALANCED | AGGRESSIVE` memory
profiles (`stgr/performance/memory-profiles.json`):

- `NORMAL` — stock Firefox behavior
- `BALANCED` — moderate background-tab suspension
- `AGGRESSIVE` — maximum background resource reduction while preserving
  usability and the protections above

## Testing

`docs/performance.md` + the benchmark harness measure background activity with
10+ tabs before/after enabling Gaming Mode. The Gaming Mode test verifies
reduced background activity **without breaking the active tab** — no invented
improvements.
