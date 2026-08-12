# Tracking Firefox Stable

STGR tracks the latest **Mozilla Firefox Stable** — never intentionally
falling far behind. The upstream basis is the `release` branch of the official
repository: `https://github.com/mozilla-firefox/firefox`.

## Source of truth

| Item | Value |
|---|---|
| Repository | `https://github.com/mozilla-firefox/firefox` |
| Branch | `release` (stable) |
| Tags | `FIREFOX_<maj>_<min>[_<patch>]_RELEASE` |
| Pinned version | `stgr-config.json` → `firefox.upstream_version` |

## Update flow

1. `python scripts/update_firefox.py check` — compares pinned vs latest.
2. `python scripts/update_firefox.py sync` — clones/fetches the source.
3. `python scripts/apply_patches.py apply` — rebases the STGR series.
4. **On conflict: STOP.** `update_firefox.py update` writes
   `automation/firefox-<version>/firefox-update-report.md` listing failed
   patches and files needing manual review.
5. Build + test + benchmark, then release. **No release with unresolved
   conflicts.**

Run `python scripts/update_firefox.py update` to perform steps 1–4 and open
the update PR manually (never auto-merged; CI must pass). Security patch
releases (same major.minor, bumped patch) are marked **SECURITY UPDATE** and
prioritized.

## Rebase etiquette

- Prefer small patches (context drift is normal; big patches are pain).
- Update `stgr/config/preferences/*.js` and its patch block together —
  `lint_prefs_sync.py` enforces it.
- After a rebase, re-run `build_stgr.py --verify-prefs-sync` and the privacy
  test: Firefox occasionally adds new telemetry subsystems.

## Rollback

`.stgr/state.json` keeps:

```
LAST_KNOWN_GOOD_FIREFOX
LAST_KNOWN_GOOD_STGR
```

If an update breaks STGR, return to the last known-good revision — a
release-engineering decision, never an automatic downgrade for installed
users. The previous stable release remains available on GitHub Releases.
