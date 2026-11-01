# Agent state

Machine-readable-ish snapshot of reality. Update this when you stop working. If this file
disagrees with the code, this file is stale — fix it.

**Last updated:** 2026-11-01
**Version:** 0.1.0 (pre-release, never tagged)
**Target:** Windows 10/11 x64 only

---

## Status

| Area | State | Verified how |
|---|---|---|
| Brand identity (`brand.json`) | Done | `scripts/check-brand.py` passes |
| Icon pipeline (ico/icns/png) | Done | Generated locally, structure asserted in CI |
| New Tab Page | Done, visually reviewed | Rendered headless at 1440×900 |
| Theme extension | Written | Manifest reviewed, not loaded in a real browser |
| Shield extension + DNR rules | Written, 98 rules compiled offline | Rule shape asserted in CI |
| Flags / profiles | Done | `--print-flags` output reviewed for balanced + lowmem |
| Preferences / policies | Written | Not yet applied to a live profile |
| Build orchestrator | Written | `py_compile` + flag parsing only |
| NSIS installer | Written | **Never compiled successfully yet** — see run 1 below |
| CI `validate` job | **Green** | Run 41279651720, all 13 steps passed |
| Release workflow | Written | Never executed (needs a tag or a main push) |
| Stage 2 patch series | Scaffolded only | No patches written yet |

### The honest summary

`ci / validate` is green on `main`. Everything downstream of it — the installer build, the
release — has still never completed. Expect the first `build-windows` run to fail on
something small; that is what it is there to find.

---

## What to do first (next session)

1. **Push and watch `ci`.** Fix whatever fails. Do not add features until `validate` and
   `installer-dryrun` are green.
2. **Run `build-windows` via `workflow_dispatch`** with `publish` off. Confirm the installer
   is ~95–120 MB and `build/app/stgr-build.json` shows a real engine revision.
3. **Install it on a clean Windows VM.** The four checks that matter:
   - NTP renders with the torii/pagoda background and five tiles
   - search box navigates
   - an ad-heavy site is visibly cleaner than in Edge
   - `chrome://policy` shows all keys `OK`
4. **Pin the base.** Copy the resolved revision + sha256 from the job summary into
   `config/base.lock.json` and commit.
5. **Only then** consider tagging `v0.1.0`.

---

## Known gaps

- **`extensions/stgr-theme` is unproven.** MV3 themes are supported, but whether an unpacked
  theme loaded via `--load-extension` is honoured by a given Chromium revision is not
  guaranteed. If the chrome stays default-grey, the fallback is
  `--force-dark-mode` plus `browser.theme.color_scheme = 0`, which is already in the seeded
  prefs. Verify before claiming "STGR Dark Theme" works.
- **The NTP link rail is cosmetic across navigation.** It only exists on the new tab page.
  Real chrome needs Stage 2 patch `0006`.
- **No updater.** Users must re-download. Documented in ROADMAP.
- **Unsigned binaries.** SmartScreen warns on first run.
- **`latest.json` is written but nothing consumes it yet.** It exists so the future updater
  has a stable contract.
- **`patches/` is empty apart from a README and `series`.** Stage 2 has not started.

---

## Decisions that are still open

| Question | Current answer | Revisit when |
|---|---|---|
| Should `balanced` enable `--process-per-site`? | No. Site isolation wins. | A memory benchmark shows the gap is larger than 30% |
| Is disabling Safe Browsing acceptable? | Yes, with local blocklists. | Phishing complaints appear |
| NSIS or MSI? | NSIS `.exe`. Per-user, no UAC. | Enterprise deployment is requested |
| Windows only? | Yes, deliberately. | There is a maintainer for another platform |
| DuckDuckGo as default search? | Yes. | A better privacy-respecting default appears |

---

## Session log

### 2026-11-01 (b) — first CI run, three fixes
**Done:** pushed to `github.com/Sensei002/stgr-browser`. `ci / validate` green (13/13).
`ci / installer compiles` failed at the NSIS step and was fixed:
- **Root cause:** the stub compile passed `$PWD` to `makensis.exe`. Git Bash gives a POSIX
  path (`/d/a/repo/repo/...`) which a native Windows binary cannot resolve. Switched to
  relative paths. This is the single most likely bug class in any `shell: bash` step that
  invokes a Windows executable — check for it first.
- **Also fixed:** the DNR budget was 75 000 rules, above Chromium's
  `GUARANTEED_MINIMUM_STATIC_RULES` of 30 000. Above that, rules compete for a global pool
  and can be dropped silently — indistinguishable from "blocking stopped working". Budget
  lowered to 30 000, and overflow is now sampled evenly across the sorted remote list instead
  of truncated (a prefix cut would have kept only domains starting with `a`–`c`).
- **Also added:** `build-windows` now runs on pushes to `main` as well as tags, so the
  installer is built on every merge rather than discovered broken at release time. Publishing
  remains gated on `ref_type == 'tag'`.
**Left:** `build-windows` has not completed a run. That is the next thing to verify.
**Landmines:** none new, but see the POSIX-path note above — it will recur.

### 2026-11-01 (a) — initial scaffold
**Done:** brand.json + icon pipeline; NTP (HTML/CSS/JS) with torii/pagoda scene; theme and
shield extensions; flags/prefs/policies/blocklists; `scripts/build.py` (fetch → assemble →
NSIS package); C# launcher with `--stgr-lowmem` and `--stgr-quit`; CI + release workflows;
full docs set including four ADRs.
**Left:** nothing had been executed in CI.
**Landmines:** see the Landmines section in [AGENTS.md](../AGENTS.md). The two that will bite
first are (a) `initial_preferences` only affecting fresh profiles, and (b) `--disable-features`
not merging across duplicate switches.
