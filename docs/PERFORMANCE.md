# Performance and memory

Everything here is a trade-off. This document exists so that no one has to guess which
trade-off was made, or why, before changing it.

Two profiles ship:

| Profile | Entry point | Philosophy |
|---|---|---|
| `balanced` | normal shortcut | Keep Chromium's site isolation. Win memory from discarding, not from merging processes. |
| `lowmem` | "STGR Browser (Low RAM)" shortcut | Trade process isolation for roughly a third less memory. Explicit, opt-in, documented. |

Both are defined in [`config/flags/flags.conf`](../config/flags/flags.conf). `lowmem` is
`balanced` plus a delta; `build.py` computes and embeds both.

---

## The memory model, briefly

Chromium's memory goes roughly:

```
  browser process            ~120 MB   (UI, network service, GPU broker)
+ one renderer per site      ~60-150 MB each
+ GPU process               ~80-200 MB (scales with resolution and canvases)
+ utility processes         ~20 MB each (audio, storage, network)
+ bfcache                   holds whole page trees for instant back/forward
+ prerender / prefetch      speculative pages held in memory
```

The levers, in descending order of impact:

1. **How many renderers exist.** `--process-per-site` collapses every tab of the same site
   into one renderer. `--renderer-process-limit` caps the total.
2. **Whether background tabs stay alive.** High Efficiency Mode discards tabs under memory
   pressure; aggressive mode discards sooner.
3. **Whether history is cached in RAM.** `BackForwardCache` is excellent for navigation
   speed and expensive for memory — it can hold dozens of full page trees.
4. **Speculative work.** Prerender and speculation rules pre-execute pages you may never
   visit.

Smoothness is a different axis: GPU rasterisation, zero-copy, and raster thread count. Those
cost VRAM, not RAM, and are cheap. Keep them on.

---

## Switch-by-switch rationale

### Telemetry and background chatter

| Switch | Mechanism | Risk |
|---|---|---|
| `--disable-background-networking` | Stops the browser process from polling for component updates, variations, and safe-browsing pings when idle. | Blocklist/CRLSet updates stop too. Accepted: our blocklist ships in the binary. |
| `--disable-component-update` | Component updater never runs. | Same as above, plus the PDF/CRL components go stale. |
| `--disable-domain-reliability` | No DNS failure reporting to Google. | None. |
| `--disable-breakpad`, `--disable-crash-reporter` | Crash handler not registered. | We get no crash reports. Deliberate. |
| `--metrics-recording-only` | Records metrics locally, never uploads. | None. Pairs with the `MetricsReportingEnabled=false` policy. |
| `--no-pings` | Drops the `<a ping>` beacon. | None. |
| `--disable-sync` | No Google account sync. | Users cannot sync bookmarks across devices. Deliberate. |
| `--disable-client-side-phishing-detection` | No Safe Browsing URL lookups. | **Real security trade-off.** Blocking still happens locally via stgr-shield; phishing protection does not. Documented in PRIVACY.md. |

### Rendering smoothness

| Switch | Mechanism |
|---|---|
| `--enable-gpu-rasterization` | Rasterises tiles on the GPU instead of the CPU. The single biggest perceived-smoothness win on scrolling. |
| `--enable-zero-copy` | Avoids a CPU copy when uploading raster tiles. |
| `--enable-native-gpu-memory-buffers` | Zero-copy path for video and canvas. |
| `--enable-accelerated-video-decode` | Hardware video decode. Big win for Twitch/YouTube, which is the audience. |
| `--enable-smooth-scrolling` | Chromium's smooth scroll animation. |
| `--num-raster-threads=4` | Matches the common 4-core target. Higher values starve the main thread on low-end machines. |
| `--enable-features=CanvasOopRasterization` | Canvas rasterises out-of-process, so a heavy canvas does not block the compositor. |
| `--enable-features=ParallelDownloading` | Splits large downloads across connections. |

### Network

| Switch | Mechanism | Risk |
|---|---|---|
| `--enable-quic` | HTTP/3. | None on modern networks. |
| `--dns-over-https-mode=automatic` | DoH when the resolver supports it. | Some captive portals misbehave; `automatic` falls back. |
| `--disable-features=OptimizationHints,...` | No page-load prediction model download, no feed suggestions, no media router discovery, no Privacy Sandbox UI, no autofill server calls. | Loses "pages you might visit" preloading. That is the point. |
| `--disable-features=Translate` | No translation service calls. | Users lose built-in translate. Re-enable by removing it from the list if requested. |

### Disk

| Switch | Value | Why |
|---|---|---|
| `--disk-cache-size` | 256 MB balanced / 128 MB lowmem | Chromium's default scales with free disk and can reach 1 GB+. A gaming machine has better uses for the space. |
| `--media-cache-size` | 64 MB | Media cache is rarely re-read. |

### Memory (the `lowmem` delta)

| Switch | Effect | Cost |
|---|---|---|
| `--process-per-site` | One renderer per site instead of per tab. **The big one.** | Loses per-tab process isolation. A compromised renderer now covers every tab of that site. This is why it is not the default. |
| `--renderer-process-limit=4` | Hard cap on renderer processes. | Excess tabs share or queue. |
| `--enable-low-end-device-mode` | Chromium's own low-end heuristics: smaller caches, fewer raster threads, reduced image decode budget. | Slightly softer scrolling on heavy pages. |
| `--js-flags=--max-old-space-size=1024` | Caps the V8 heap at 1 GB per renderer. | A pathological page OOMs earlier instead of eating the machine. |
| `--disable-features=BackForwardCache` | Stops whole page trees being held for instant back. | Back navigation is a real reload. Typically 150–400 MB saved with a dozen tabs. |
| `--disable-features=Prerender2,SpeculationRulesPrefetchFuture` | No speculative page execution. | No instant-load on hover/likely-next links. |

Measured on a 16 GB Windows 11 machine, 12 tabs (YouTube, Twitch, GitHub, Discord, docs):

| Profile | Private bytes | Renderers |
|---|---|---|
| Chromium default | ~2.9 GB | 14 |
| `balanced` | ~1.9 GB | 10 |
| `lowmem` | ~1.3 GB | 4 |

These are indicative, not a benchmark suite. Treat them as direction, not spec.

---

## Preferences that matter

Flags are not the only lever. `config/preferences/stgr-defaults.json` seeds the profile
once, on first run:

- `performance_tuning.high_efficiency_mode.state = 2` — aggressive tab discarding.
- `net.network_prediction_options = 2` — no prefetch, no preconnect.
- `profile.default_content_setting_values.autoplay = 2` — blocked. Stops video ads from
  starting and stops background tabs from decoding video.
- `search.suggest_enabled = false` — no keystroke leakage to the search engine.
- `signin.allowed = false`, `sync.requested = false` — no account surfaces.
- `credentials_enable_service = false`, `autofill.* = false` — no password manager or
  autofill prompts; they cost startup time and a surprising amount of memory.

Remember: **these only apply to a brand-new profile.** To test a change, delete
`%LOCALAPPDATA%\STGR\Browser` first.

---

## How to measure a change

Do not trust feel. Use the browser's own instrumentation:

```
chrome://memory-internals     per-process breakdown, live
chrome://histograms           Memory.* histograms after a session
chrome://discards             per-tab discard state and lifecycle
chrome://gpu                  which rasterisation path actually engaged
```

Procedure for a flag change:

1. Fresh profile, same 12 URLs, same window size.
2. Let the machine idle 60 s so discarding settles.
3. Record `chrome://memory-internals` total private bytes and renderer count.
4. Change exactly one switch. Repeat.
5. Put the number in the table above with the date. A flag without a number is an opinion.

---

## Banned switches

These make the browser *feel* faster while burning battery and CPU. They are explicitly
not allowed in any profile:

- `--disable-renderer-backgrounding` — background tabs render at full speed forever.
- `--disable-background-timer-throttling` — timers in hidden tabs stop being throttled.
- `--disable-backgrounding-occluded-windows` — same problem, window-level.

A gaming browser competes for the same GPU the game is using. Trading idle efficiency for
imperceptible responsiveness is the wrong trade here.
