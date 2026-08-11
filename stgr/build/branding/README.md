# STGR Build Branding Directory

This directory is what `--with-branding` points at (see
`stgr/build/mozconfig.windows-x64-release`). Firefox's branding machinery reads
the product name, version metadata, and icons from here.

## Contents

| File | Purpose |
|---|---|
| `brand.ftl` / `brand.dtd` / `brand.properties` | Product name strings |
| `configure.sh` | Branding identity (app name, vendor, profile dir, app id) |
| `firefox.ico` + `default{16,32,48,64,128,256,512}.png` | Application icons — **generated** by `scripts/make_icons.py` from the master logo (`stgr/branding/stgr-logo.png`), staged by `build_stgr.py prepare` |

The icon files are derived assets and are **not** committed — they are produced
from the official logo during `prepare`. Until the official logo is provided,
`python scripts/make_icons.py --generate-placeholder` creates test-only stand-ins.

## App identity notes

- `MOZ_APP_ID` keeps the upstream Firefox id for extension compatibility
  (WebExtension `applications.gecko.id`).
- Profile location is `%APPDATA%\STGR\STGR Browser\Profiles` — deliberately
  distinct from Mozilla Firefox's `%APPDATA%\Mozilla\Firefox`. STGR never
  reads or writes Firefox user data; importing from other browsers is an
  explicit, opt-in first-run flow only.
- `MOZ_APP_NAME=stgr` → the executable is `stgr.exe`.
