# STGR Patch Series

Every modification STGR makes to upstream Firefox lives here as a small, ordered, documented
patch. **Prefer configuration over patches** — if a change can be a preference or a branding-file
swap (`--with-branding`), it is not a patch.

## Series order (file: `series`)

1. `0001-stgr-branding.patch` — branding strings, upstream attribution, update channel
2. `0002-stgr-privacy-defaults.patch` — telemetry off + core STGR preference block
3. `0003-stgr-new-tab.patch` — lightweight New Tab + About pages, `resource://stgr` mapping
4. `0004-stgr-gaming-mode.patch` — Gaming Mode module + performance preference block
5. `0005-stgr-ui.patch` — chrome CSS (dark dojo theme, compact tabs, red accents)
6. `0006-stgr-update-system.patch` — STGR updater module + update preferences wiring

## Patch header format

Every patch begins with a comment block:

```text
STGR PATCH: <title>
Purpose:                …
Files changed:          …
Security impact:        …
Performance impact:     …
Upstream compatibility: …
```

## Ground rules

- **Small patches.** If a patch grows past ~150 lines, split it.
- **Never weaken security.** Patches must not touch sandboxing, process isolation, certificate
  validation, or anti-exploitation code.
- **Never remove upstream copyright notices.**
- **Markers stay in sync.** The preference blocks injected by 0002/0004 are the exact content of
  `stgr/config/preferences/*.js`. `scripts/build_stgr.py --verify-prefs-sync` enforces this.
- **0003 stages the UI, it does not embed it.** The patch only wires the moz.build
  (`RESOURCE_FILES` -> `resource://gre/res/stgr/…`, `DIST_SUBDIR = ""`, `DIRS` for 0004/0006) and
  the `AboutNewTabRedirector` hook. The actual page files (`newtab/*`, `about/aboutStgr.html`) and
  the official logo are staged by `build_stgr.py prepare` into
  `browser/components/stgr/res/stgr/…` from `stgr/ui/` + `stgr/branding/`, so the shipped build
  always uses the current master copies.
- Diffs are canonical drafts against the Firefox version pinned in
  `stgr/config/stgr-config.json` (`firefox.upstream_version`). Firefox moves fast — expect context
  to drift; that is normal and handled by the rebase machinery, not by force-applying.

## Conflict policy

When a Firefox update makes a patch fail to apply:

1. **STOP.** Do not `--force` or fuzz it into place.
2. `python scripts/update_firefox.py` writes `firefox-update-report.md` with the failing patch and
   the files needing manual review.
3. Rebase the patch by hand, verify the block still matches `stgr/config/preferences/*.js`,
4. Re-run build + tests. **No release ships with unresolved conflicts.**

## Tooling

```bash
python scripts/apply_patches.py check   # dry-run apply; report conflicts
python scripts/apply_patches.py apply   # apply the series in order
python scripts/apply_patches.py status  # which patches are applied
```
