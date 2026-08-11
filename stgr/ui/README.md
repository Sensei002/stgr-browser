# STGR UI Resources

Lightweight, native, dependency-free UI assets that ship inside the browser as local
`resource://stgr/…` pages.

| Path | Purpose | Notes |
|---|---|---|
| `newtab/newtab.html` + `.css` + `.js` | Default New Tab page | Fully offline; clock, search, custom shortcuts (localStorage). No network, no ads, no telemetry. |
| `about/aboutStgr.html` | STGR About page | Shows STGR + upstream Firefox versions, org, open-source badge, update/release/source/license/privacy links. |

## How these reach the browser

1. `patches/0003-stgr-new-tab.patch` registers the `resource://stgr/` mapping and points
   `browser.newtabpage.activity-stream.overrideURL` + the homepage at the New Tab page.
2. `scripts/build_stgr.py` performs template substitution (`{{SEARCH_URL}}`, `{{STGR_VERSION}}`,
   `{{FIREFOX_VERSION}}`, `{{UPDATE_URL}}`, …) using `stgr/config/stgr-config.json` and writes the
   final assets into the Firefox source tree before the build.

## Design rules

- Dark red/black dojo aesthetic (see `stgr/branding/brand.json`).
- Red is an **accent** — avoid excessive red.
- No JavaScript frameworks. No external resources. These pages must work offline.
- The Firefox chrome UI itself is styled via `patches/0005-stgr-ui.patch` (CSS overrides in the
  browser chrome); we never replace the whole UI with a web app.
