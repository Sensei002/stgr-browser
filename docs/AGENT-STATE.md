# Agent state

Machine-readable-ish snapshot of reality. Update this when you stop working. If this file
disagrees with the code, this file is stale — fix it.

**Last updated:** 2026-11-01
**Version:** 0.1.1
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
| Build orchestrator | Done | Full run green in CI, run 41280347362 |
| NSIS installer | **Works** | 253,749,352 bytes, sha256 `94a10edb…` |
| CI `validate` job | Green | Run 41279651720 |
| `ci / installer compiles` | Green | Run on `a1b7472` |
| Release workflow | Written, untested | Needs a tag; publishing path never executed |
| Stage 2 patch series | Scaffolded only | No patches written yet |

### The honest summary

Both workflows are green on `main`. The Windows installer **builds end to end in CI** —
`STGR-Browser-Setup-0.1.0-x64.exe`, 242 MiB, from a cold cache in about 9 minutes, with
rcedit branding, the compiled launcher, and all three extensions staged.

Two things this does *not* prove:

1. **The installer has never been run.** Build success is not launch success. Install it,
   launch it, check the four items in "What to do first".
2. **Builds are not bit-reproducible.** Two builds of the same commit produced different
   sha256 values (`94a10edb…` then `b1569597…`). NSIS embeds a timestamp and
   `config/base.json` still resolves `latest`. Pin `base.lock.json` before treating a hash
   as an identity.

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

### 2026-11-01 (e) — startup tab, take two
0.1.1 fixed the icon and the theme, but the first tab *still* showed Chromium's built-in new
tab page. The 0.1.1 screenshot also proved the theme extension works: the toolbar came up
`#20090D` maroon, which is ours, not Chromium's default dark.

So the remaining bug was narrower than assumed. `chrome_url_overrides` is **not consulted
when Chromium builds the startup tab** — it creates that tab from the startup preference
before the extension registry is ready. Every *new* tab got the override; the first one never
could.

Fix: the launcher now appends the new-tab URL to the engine command line when the user
supplied no URL of their own. A URL on the command line replaces the startup pages entirely
and is navigated after extensions register, so exactly one tab opens and it is always ours.
`restore_on_startup` stays at 5 as a fallback for anyone launching `stgr.exe` directly.

**Second bug, found by the new `--dump-launcher`:** `parse_flags()` stored switches in a
dict, so a profile's own `--disable-features` line replaced the shared one instead of
merging with it. `lowmem` was silently re-enabling every AI feature that `balanced` disabled.
Feature switches now accumulate across `@include` layers. This is the argument for keeping
that dump command: it made a silent regression visible without a compiler.

**Version:** 0.1.2.

### 2026-11-01 (d) — first real install, four user-reported bugs
The installer was run on real Windows. It launched, and three defects were immediately
visible. This is the most valuable feedback the project has had; treat "it built" as
unproven until someone has launched it.

1. **First tab showed Chromium's built-in NTP, not STGR.** Root cause: two preferences
   pointed the new tab at `stgr://newtab/`, a scheme Chromium has no internal handler for.
   New tabs worked (they go through `chrome_url_overrides`), the startup tab did not.
   Fix: `homepage` is now the real `chrome-extension://…/index.html`, and
   `newtab_page_location_override` is gone. `scripts/check-brand.py` now fails the build if
   either regresses.
2. **No app icon.** `csc` emits an iconless exe, and only the engine was being stamped, so
   the desktop shortcut showed the generic "unknown file" icon. Fix: `stamp_binary()` now
   runs on `STGRBrowser.exe` too, and the build **fails** if it cannot stamp it.
3. **Chrome looked unthemed.** The old theme was `#08080A`/`#101014` — indistinguishable
   from plain dark mode. Toolbar is now `#20090D` and the frame is warm-black, so the tint
   is visible. `BrowserThemeColor` / `BrowserColorScheme` policies were added as a fallback
   in case the unpacked theme is not honoured.
4. **AI surfaces.** Added a documented `--disable-features` block for Compose, AI history
   search, on-device model downloads, AI wallpaper, AI autofill and the NTP footer.
   Chromium ignores unknown feature names, so the list is safe to over-specify.

**Also done:** the NTP extension now carries a `key`, giving it the stable ID
`hpdfacponigkmgcehdnobgkojchgoijg`. Without it the ID is derived from the unpacked path, so
`chrome-extension://` URLs and profile storage would move between installs.

**Version:** bumped to 0.1.1. `v0.1.0` was tagged, the tag run was cancelled before it
published, and the tag was deleted — it shipped the three defects above.

**Still unproven:** whether the theme extension is honoured at all when loaded unpacked via
`--load-extension`. If the chrome is still neutral grey after 0.1.1, the policy fallback is
the only remaining lever without a source build, and a custom toolbar becomes Stage 2 work.

### 2026-11-01 (c) — installer builds in CI
**Done:** `build-windows` #3 green. `STGR-Browser-Setup-0.1.0-x64.exe`, 253,749,352 bytes,
sha256 `94a10edbc9d24b237f60b001f28a24e49e989f8599b857a1b4b5fd39d8f60ea0`. Engine
resources stamped, launcher 11 KiB, 294 entries staged, 30 balanced switches + 6 low-RAM.
Three separate CI failures were fixed to get here:
1. `setup-python` with `cache: pip` and no dependency file kills the job at step 3. Added
   `requirements-build.txt` and `cache-dependency-path`.
2. NSIS is not at `C:\Program Files (x86)\NSIS` until `choco install nsis` runs.
3. Git Bash rewrote `/V3` into `C:/Program Files/Git/V3`, so `makensis` tried to compile a
   file that does not exist. Needs `MSYS_NO_PATHCONV=1`.
**Left:** the installer has never been run on Windows. Install it, launch it, and check the
four things in "What to do first". Also: 242 MiB is large — a snapshot build carries a lot
that an official `is_official_build` build would not. Do not optimise size before Stage 2.
**Landmines:** the MSYS path-conversion one is now in AGENTS.md. It will bite again in any
`shell: bash` step that calls a Windows binary with `/` switches.

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
