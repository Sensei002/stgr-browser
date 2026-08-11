# STGR Branding

This directory holds the STGR brand identity for **STEiGER Dojo**'s STGR Browser.

## Master logo

The **official** STEiGER Dojo logo is committed here:

| File | Purpose | Status |
|---|---|---|
| `stgr-logo.svg` | Vector master (preferred source) | ✅ Official (2048×1728) |
| `stgr-logo.png` | Raster master used for icon generation | Optional — derived from the SVG via cairosvg if absent |

Do not modify the logo artwork unless explicitly requested. The SVG ships into the browser
UI (New Tab, About) via patch 0003 and `build_stgr.py prepare`; raster icons are generated
from it by `make_icons.py` (non-square masters are center-fitted with transparent padding).

## Icon set

`scripts/make_icons.py` derives every icon the browser needs from the master logo:

- `icons/icon-{16,24,32,48,64,128,256,512}.png` — used for About page, New Tab page, UI, installer
- `icons/stgr.ico` — multi-resolution Windows icon (executable, shortcuts, taskbar)

The **generated set is committed** (so builds work without Pillow/cairosvg). To regenerate
(always keep the committed set in sync with the master):

```bash
python scripts/make_icons.py            # regenerate from the official master logo
python scripts/make_icons.py --generate-placeholder   # test the pipeline without a logo
```

The build step (`build_stgr.py prepare`) copies these into the Firefox branding directory
configured in `stgr/build/mozconfig.windows-x64-release` (`--with-branding`).

## Where branding appears

Window title · About page (`stgr/ui/about/`) · Installer · Application metadata · Desktop/Start
Menu shortcuts · File-association info · Browser UI · Settings · Update UI · Error pages ·
Application icons · Executable resources.

Branding is applied through:

1. `stgr/config/stgr-config.json` + `stgr/branding/brand.json` — single sources of truth.
2. `patches/0001-stgr-branding.patch` — replaces Firefox branding files at build time.
3. `stgr/build/branding/` — the branding directory contents referenced by the mozconfig.

## Colors

See `brand.json`. Primary: black `#080808`, dark black `#0D0D0D`, STGR red `#E8202A`
(accent only), dark red `#8F1018`, optional gold `#C8A45D`.

## Attribution

STGR Browser is *based on Mozilla Firefox* and must always be identified as such where
appropriate. Firefox/Mozilla trademarks remain Mozilla's. Do not misrepresent STGR as official
Mozilla software.
