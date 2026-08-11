# STGR Browser — Architecture

## Principle

STGR is a **genuine Firefox/Gecko source build** — not Electron, not a
wrapper, not a frontend on top of Firefox. All STGR modifications are a thin,
identifiable layer over the latest stable Firefox source.

```
Mozilla Firefox Stable (pinned release tag, e.g. FIREFOX_153_0_RELEASE)
        ↓  (git, pinned upstream version)
STGR patch/configuration layer   ← this repository
        ↓
STGR build  →  STGR tests  →  STGR release
```

## Repository layout

```
stgr-browser/
├── firefox/            ← Firefox upstream source (git, NOT committed here)
├── stgr/
│   ├── branding/       ← brand.json (design tokens) + logo assets + icons/
│   ├── config/         ← stgr-config.json + preference layers (canonical)
│   ├── ui/             ← New Tab, About page, chrome CSS (canonical copies)
│   ├── privacy/        ← privacy architecture notes
│   ├── performance/    ← memory profiles + design notes
│   ├── updater/        ← updater architecture notes
│   ├── extensions/     ← uBlock Origin XPI + integration docs
│   ├── resources/      ← shared static assets policy
│   └── build/          ← mozconfig, branding dir, manifest template
├── patches/            ← the STGR patch series (ordered, documented)
├── scripts/            ← automation (stdlib Python, no pip for core)
├── benchmark/          ← harness config + baselines
├── automation/         ← per-update work dirs + reports (gitignored)
├── docs/               ← this documentation set
└── .github/workflows/  ← CI/CD
```

## Layer rules

1. **Config over code.** Functionality that can be a preference or a branding
   swap lives in `stgr/config/` or `stgr/build/branding/` — not in a patch.
2. **Every Firefox change is a patch.** Small, ordered, documented; conflicts
   stop the release.
3. **Canonical copies.** `stgr/ui/` and `stgr/config/preferences/` are the
   canonical files; patches/build inject them into the tree. `lint_prefs_sync.py`
   and `build_stgr.py --verify-prefs-sync` keep them honest.
4. **Single source of truth.** `stgr/config/stgr-config.json` drives scripts,
   CI, and release naming.

## Versioning

Two versions are always displayed separately (About page, manifest):

- **STGR version** — `MAJOR.MINOR.PATCH`, e.g. `1.0.0`
- **Firefox upstream** — e.g. `153.0`, pinned in `stgr-config.json`

`build-manifest.json` records both plus commit/revision/toolchain for
reproducibility (§72–73).

## Update model

`scripts/update_firefox.py` tracks the official repository
(`github.com/mozilla-firefox/firefox`):

- `check` — compare pinned upstream against latest stable
- `sync` — clone/fetch the source **at the pinned release tag**
  (`FIREFOX_<version>_RELEASE`, deterministic; never the moving
  `release` branch tip, so the patch series always applies)
- `update` — sync → apply patches → (build/test) → `firefox-update-report.md`

A failed patch means: **stop, fix, verify** — never force. Rollback keeps
`LAST_KNOWN_GOOD_*` in `.stgr/state.json`; downgrading installed users is a
release-engineering decision, never automatic.

## Channels

v1 targets **Stable only**. The layout leaves room for Nightly/Beta later, but
they are out of scope until Windows Stable is reliable.

## Profile isolation

STGR uses its own profile identity (`%APPDATA%\STGR\STGR Browser\Profiles` via
the branding `configure.sh`) and never touches Mozilla Firefox user data.
Importing from Firefox/Chrome/Edge is an opt-in first-run flow only.
