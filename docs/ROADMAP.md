# Roadmap

Stage 1 is done and automated. Everything below is Stage 2 or later, ordered by
value-per-unit-of-risk. Read [ADR-0002](decisions/ADR-0002-build-strategy.md) first — it
explains why the split exists.

---

## Stage 2 — fork the engine

**Goal:** own the product strings, the chrome UI, and the defaults at compile time instead of
injecting them after the fact.

**Blocker:** a Chromium source build needs roughly 100 GB of disk, 32+ cores and 6+ hours.
`windows-latest` has 14 GB free and 4 cores. This cannot run on a hosted runner at any
configuration. It needs a self-hosted runner.

### 2.1 Self-hosted build runner

- Windows Server 2022, 32 vCPU, 64 GB RAM, 500 GB NVMe.
- `depot_tools` on PATH, `gclient` configured for `src` at the pinned tag.
- Registered as a repo-scoped self-hosted runner with label `chromium-builder`.
- Workflow: `.github/workflows/build-from-source.yml` (scaffolded, `workflow_dispatch` only).

### 2.2 Patch series

`patches/series` is the ordered list. Each patch is a `git format-patch` against
`chromium/src`. The first three are the ones that matter:

| Patch | File | Effect |
|---|---|---|
| `0001-branding-strings` | `chrome/app/theme/chromium/BRANDING` | Product name, vendor, copyright compiled in |
| `0002-branding-assets` | `chrome/app/theme/chromium/` | Real `.ico` / `.icns` / PNG set replaces Chromium's |
| `0003-default-prefs` | `chrome/browser/prefs/browser_prefs.cc` | Privacy and performance defaults baked in, so they apply to *every* profile, not just new ones |
| `0004-disable-telemetry` | `components/metrics/`, `chrome/browser/upgrade_detector/` | Remove reporting call sites rather than configuring them off |
| `0005-custom-toolbar` | `chrome/browser/ui/views/frame/` | The mockup's toolbar: rail toggle, shield button, brand colouring |
| `0006-sidebar-rail` | `chrome/browser/ui/views/side_panel/` | Promote the NTP's link rail to real chrome |

`0003` is the highest-value patch. It is the difference between "privacy on new profiles"
and "privacy on all profiles" — the current `initial_preferences` mechanism cannot reach an
existing profile.

### 2.3 Build cost control

- `gclient sync` with `--no-history`, shallow.
- `is_component_build = false`, `is_official_build = true`, `symbol_level = 0`,
  `blink_symbol_level = 0`.
- `use_thin_lto = true` — cuts link time roughly in half for a small size cost.
- Cache `chromium/src/out` between runs keyed on `patches/series` hash. An incremental
  branded build lands around 40–70 minutes once the object cache is warm.

---

## Stage 3 — product completeness

| Item | Why | Notes |
|---|---|---|
| Auto-update | A browser without updates is a liability | Omaha-style updater is a large project. Minimum viable: a signed `latest.json` check on startup plus a relaunch prompt. |
| Code signing | Removes the SmartScreen wall | See [RELEASE.md](RELEASE.md#code-signing) |
| Profile import | Users arriving from Chrome expect bookmarks | `--import-bookmarks` is off today; the UI needs a deliberate flow |
| Crash reporting (opt-in) | We currently get zero signal | Contradicts the privacy stance unless it is explicit, local-first, and off by default |
| Per-site shield toggles | Blocking occasionally breaks a site | The popup has the toggle; it needs a per-origin allowlist |
| Vertical tabs | Gaming audience, wide screens | Upstream has the flag; it needs styling to match the theme |

---

## Explicitly not planned

- A sync service. It requires accounts and a backend, and it is the single biggest source of
  privacy surface in a browser.
- An extension store. Chrome Web Store works.
- A mobile build. Different engine integration entirely.
- A built-in VPN. It is a subscription product wearing a browser costume.

---

## How to pick up work

1. Read [AGENT-STATE.md](AGENT-STATE.md) for what is actually true right now.
2. Pick the top unblocked item.
3. If it needs a decision someone might reverse, write the ADR first.
4. Update the state file when you stop.
