# STGR Configuration Layer

This is the central, single-source-of-truth configuration for STGR Browser (§30 of the
engineering spec). STGR constants are **not** scattered across hundreds of Firefox files.

## Files

| File | Contents |
|---|---|
| `stgr-config.json` | All functional constants: product/version, Firefox upstream, defaults, build, uBlock, privacy allowlist, release naming, benchmark thresholds |
| `branding/brand.json` | Visual identity / design tokens (colors, logo paths, typography) |
| `preferences/stgr.js` | Core pref layer (branding strings, new tab, search, gaming/memory defaults) |
| `preferences/privacy.js` | Telemetry-off and network-privacy prefs |
| `preferences/performance.js` | Performance defaults and memory-profile presets |

## How preferences reach the browser

The preference files here are the **canonical, reviewable copies**. At build time the same
content is injected into Firefox's `browser/app/profile/firefox.js` by the STGR patch series
(`patches/0002` and `patches/0004`), so defaults are compiled into the product.

To keep the two in sync, `scripts/build_stgr.py` runs a `--verify-prefs-sync` check that asserts
the `// BEGIN STGR ... PREFS` / `// END STGR ... PREFS` markers exist verbatim in `firefox.js`
after patching. If they drift, CI fails.

## Editing defaults

1. Edit the file here.
2. Update the corresponding patch in `patches/` (the injected block).
3. Run `python scripts/build_stgr.py --verify-prefs-sync` locally (needs a synced `firefox/` tree)
   or rely on CI (`tests.yml` runs the same check).

## Configuration contract

- `stgr-config.json` must always validate against the documented schema (see
  `stgr/build/build-manifest.template.json` for the build manifest shape produced from it).
- Never hard-code an STGR constant inside the Firefox tree — it belongs here.
