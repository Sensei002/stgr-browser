# AGENTS.md — operating contract

This file is the entry point for any AI agent (or human) taking over this repository.
It is intentionally prescriptive. Follow it and the project stays coherent; ignore it and
you will silently break the build in ways CI only catches an hour later.

---

## 1. Read in this order

1. **This file.** Non-negotiable.
2. [`docs/AGENT-STATE.md`](docs/AGENT-STATE.md) — what works right now, what is broken, what is next.
3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — the mental model.
4. The ADR that covers the area you are about to touch, in [`docs/decisions/`](docs/decisions/).
5. The specific file you are changing. Read it fully before editing.

Do not start editing after reading only the README. The README describes intent; the
state file describes reality.

---

## 2. Golden rules

These are invariants. Violating one is a bug even if the build passes.

**R1 — One source of truth.** Product name, IDs, colours, URLs and speed-dial entries live
only in `branding/brand.json`. Version lives only in `VERSION`. Launch switches live only in
`config/flags/flags.conf`. If you need a new product string, add it to `brand.json` and
thread it through — never inline it.

**R2 — Generated files are never hand-edited.** These carry a header saying so:
`ntp/config.js`, `ntp/manifest.json` (version field), `extensions/stgr-shield/rules/*.json`,
`branding/icons/**`, `overrides/windows/*.bmp`. Change the generator or the input, then
regenerate.

**R3 — The build never mutates its inputs.** `scripts/build.py` copies `build/base` into
`build/app` before touching anything. Keep it that way; a failed build must not poison the
next one.

**R4 — No compile on a developer machine.** Everything that produces a binary runs in
GitHub Actions. Local work is limited to validators and codegen. If you find yourself
needing `makensis` or `csc` locally to verify a change, add a CI check instead.

**R5 — Every flag needs a written reason.** Adding a switch to `flags.conf` without a
comment explaining the mechanism and the risk is not acceptable. See
[docs/PERFORMANCE.md](docs/PERFORMANCE.md) for the format.

**R6 — Privacy changes are breaking changes.** Anything that adds a network call, a
telemetry endpoint, a remote font, or a runtime filter-list download must be documented in
`docs/PRIVACY.md` in the same commit.

**R7 — Never weaken process isolation silently.** `--process-per-site` and friends belong
in the `lowmem` profile only, behind the explicit `Low RAM` shortcut. Moving them into
`balanced` requires an ADR.

---

## 3. Commands you will actually use

```bash
# --- validation (run before every commit; CI runs the same) -------------------
python -m compileall -q scripts branding
python scripts/check-brand.py
node --check ntp/app.js
python scripts/build.py --print-flags balanced

# --- regenerate derived assets -----------------------------------------------
python branding/generate-icons.py        # icons from branding/source/logo-original.png
python scripts/gen-installer-art.py      # NSIS wizard/header bitmaps
python scripts/gen-ntp-config.py         # ntp/config.js + extension icons + manifest version
python scripts/build-shield-rules.py     # DNR rulesets (add --offline to skip downloads)

# --- inspect the runtime configuration ---------------------------------------
python scripts/build.py --print-flags lowmem    # resolved switch list
```

`python scripts/build.py` (full build) only makes sense on Windows with `makensis` and
`csc` present — i.e. in CI. Do not add it to your local loop.

---

## 4. Where does a change go?

| You want to change… | Edit this | Then run |
|---|---|---|
| Product name, tagline, URLs, colours | `branding/brand.json` | `gen-ntp-config.py`, `generate-icons.py` |
| Speed dial tiles | `branding/brand.json` → `speedDial` | `gen-ntp-config.py` |
| New Tab Page layout or behaviour | `ntp/index.html`, `ntp/styles.css`, `ntp/app.js` | — |
| Which sites are blocked | `config/blocklists/stgr-core.txt` or `sources.json` | `build-shield-rules.py` |
| Browser chrome colours | `extensions/stgr-theme/manifest.json` | — |
| Default preferences | `config/preferences/stgr-defaults.json` | — |
| Launch switches | `config/flags/flags.conf` | `build.py --print-flags <profile>` |
| Telemetry / enterprise policy | `config/policies/base.json` | — |
| Installer behaviour, shortcuts, registry | `overrides/windows/installer.nsi` | CI `installer-dryrun` job |
| Installer artwork | `scripts/gen-installer-art.py` | that script |
| Engine version | `config/base.json` (`revision`) | — |
| App icon | `branding/source/logo-original.png` | `generate-icons.py` |

---

## 5. Definition of done

A change is done when all of these are true:

- [ ] `python scripts/check-brand.py` passes.
- [ ] `python -m compileall -q scripts branding` passes.
- [ ] `node --check` passes for every touched `.js` file.
- [ ] Any regenerated asset is committed alongside the change that caused it.
- [ ] `docs/AGENT-STATE.md` reflects the new reality.
- [ ] If you touched flags, prefs, policies, or anything network-facing: the matching doc
      (`PERFORMANCE.md` / `PRIVACY.md`) is updated **in the same commit**.
- [ ] If you made an architectural choice someone might later reverse: a new ADR exists.

---

## 6. Handoff protocol

When you finish a work session, append to `docs/AGENT-STATE.md`:

```
### <date> — <one-line summary>
Done: …
Left: …
Landmines: …
```

Be specific. "Refactored build" is useless. "Split `assemble()` so `--no-installer` stops
before packaging; `build/app` is now reusable by the QA job" is useful.

If you learned something a future agent would waste an hour rediscovering, it belongs in
`docs/AGENT-STATE.md` under **Landmines**, not in a commit message.

---

## 7. Known landmines

Read these before debugging anything.

**The engine is a renamed `chrome.exe`.** Chromium locates its resources relative to the
executable, so the rename is safe — but anything that hardcodes `chrome.exe` (scripts,
shortcuts, taskkill calls) will silently target nothing. The launcher falls back to
`chrome.exe` deliberately; do not "clean that up".

**`initial_preferences` only applies to a fresh profile.** Editing
`config/preferences/stgr-defaults.json` does nothing for anyone who has already launched the
browser. Testing a pref change requires deleting `%LOCALAPPDATA%\STGR\Browser` first. This
wastes more debugging time than any other fact in this repo.

**Never point a pref at `stgr://`.** The installer registers that scheme with the OS, but
Chromium has no internal handler for it. A `homepage` or `newtab_page_location_override`
pointing at `stgr://newtab/` makes the startup tab silently fall back to Chromium's built-in
new tab page, while new tabs still work — a confusing half-broken state. Use the real
`chrome-extension://<id>/index.html`, and let `scripts/check-brand.py` police it.

**`chrome_url_overrides` does not apply to the startup tab.** Chromium builds the first tab
from the startup preference without consulting the extension registry, so an NTP extension
that works perfectly on every *new* tab still leaves the first tab on Chromium's built-in
page. The only reliable fix in a distribution build is to hand the engine an explicit URL on
the command line, which the launcher does. Do not "simplify" that away.

**`--disable-features` accumulates, but only because `build.py` makes it.** Chromium keeps
only the last occurrence of a duplicated switch. `parse_flags()` therefore unions every
`--disable-features` line across `@include` layers before emitting one. If you add a second
feature line to a profile and the earlier list stops applying, that merge has regressed —
`python scripts/build.py --print-flags lowmem` shows the resolved list.

**A compiled launcher has no icon.** `csc` produces an iconless exe. If you add another
binary to the payload, stamp it with `stamp_binary()` or the shortcut will show the generic
"unknown file" icon.

**Theme colours must be visible, not merely correct.** A `#08080A` frame is
indistinguishable from plain dark mode, and users read that as "the theme didn't load". Push
the toolbar to a warm red-black so the tint is obvious.

**Duplicate `--disable-features` switches: last one wins, others vanish.** Chromium does not
merge them. `flags.conf` keeps one line per feature list and `build.py` merges `@include`
chains — do not add a second `--disable-features` line in a profile.

**Per-user policies live in `HKCU\Software\Policies\Chromium`, not `...\STGR`.** The binary
is upstream Chromium, so it looks for the Chromium policy path regardless of what we call
the product. Renaming that key breaks every policy silently.

**The NTP is an extension, not browser chrome.** It cannot draw the tab strip, toolbar, or
the left sidebar as real UI. The sidebar in the NTP is a link rail that disappears once you
navigate. Making it real chrome is Stage 2 work (`patches/`), not a CSS change.

**Git Bash rewrites Windows-style switches.** In any `shell: bash` step that calls a native
Windows binary, an argument like `/V3` is silently converted to `C:/Program Files/Git/V3`
before the program sees it. `makensis` then treats the mangled switch as the script path and
fails with `Can't open script "C:/Program Files/Git/V3"`. Prefix the command with
`MSYS_NO_PATHCONV=1`, or call the tool from Python (where `subprocess` does no rewriting).
This cost two CI cycles; do not rediscover it.

**Only 10 check-run annotations survive, and CI logs need admin rights to download.** When
adding a failure handler, annotate the lines that *explain* the failure, not a fixed tail
window — a `tail -40 | echo ::error::` handler gets truncated to the first ten lines and hides
the error entirely. `build.py` annotates its own `die()` and uncaught exceptions for this
reason.

**Solid LZMA makes the installer slow, not broken.** A ~250 MB payload compresses for
8–12 minutes on a 4-core runner. If the job looks hung, it is probably compressing. Check
`makensis /V3` output before assuming a hang.

**`base.lock.json` is optional but load-bearing for reproducibility.** Without it, `latest`
resolves to a different Chromium revision every build. See [docs/BUILD.md](docs/BUILD.md)
for the promotion procedure.
