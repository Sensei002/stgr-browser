# STGR Build Branding Directory

This directory is the repository source for the STGR branding files. Before
configure, `scripts/build_stgr.py prepare` copies these files and generated
icons into `firefox/browser/branding/stgr`, the in-tree directory passed to
`--with-branding`. Firefox's branding machinery reads the staged copy.

## Contents

| File | Purpose |
|---|---|
| `brand.ftl` / `brand.dtd` / `brand.properties` | Product name strings |
| `configure.sh` | Product display name consumed by Firefox's branding configure contract |
| `moz.build` | Registers the staged branding resources with Firefox's build system |
| `firefox.ico` + `default{16,32,48,64,128,256,512}.png` | Application icons — **generated** by `scripts/make_icons.py` from the master logo (`stgr/branding/stgr-logo.png`), staged by `build_stgr.py prepare` |

The icon files are derived assets and are **not** committed — they are produced
from the official logo during `prepare`. Until the official logo is provided,
`python scripts/make_icons.py --generate-placeholder` creates test-only stand-ins.

## App identity notes

- Firefox's `browser/moz.configure` supplies the upstream application ID
  (`{ec8030f7-c20a-464f-9b0e-13a3a9e97384}`), preserving WebExtension
  `applications.gecko.id` compatibility. The branding script must not override
  that implied option.
- Firefox's modern Windows build configuration owns executable and profile
  identity. STGR-specific product naming is supplied through the display name,
  brand strings, About page, and distribution assets.
