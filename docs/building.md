# Building STGR Browser on Windows x64

Building Firefox from source is heavy but fully supported. The following is
based on the current Firefox build documentation
(firefox-source-docs.mozilla.org) and the toolchain auto-detection of
`./mach bootstrap`.

## Prerequisites

| Requirement | Notes |
|---|---|
| Windows 10 or 11 (fully updated) | A Dev Drive on Windows 11 speeds up VCS/builds 5–10% |
| ~40 GB free disk | source + build artifacts (~20 GB post-build) |
| 8 GB+ RAM (16 GB recommended) | Firefox builds are memory hungry |
| Git for Windows | via MozillaBuild or standalone |
| **MozillaBuild** | `C:\mozilla-build\` — run all build commands from its shell (`start-shell.bat`) |

`./mach bootstrap` then installs/auto-detects the matching **Visual Studio C++
toolchain, Windows SDK, Rust, and Python** — do not hand-install mismatched
versions. Detect the current requirements from the Firefox source docs rather
than hard-coding versions here.

## Build commands

```bash
# 1. Sync the Firefox Stable source (clone ~first time)
python scripts/update_firefox.py sync

# 2. Bootstrap the toolchain (first time; interactive)
cd firefox
python mach bootstrap --application-choice=browser
cd ..

# 3. Verify + apply the STGR patches
python scripts/apply_patches.py check
python scripts/apply_patches.py apply

# 4. Configure + build (uses stgr/build/mozconfig.windows-x64-release)
python scripts/build_stgr.py build

# 5. Package installer + portable archive + SHA256SUMS + manifest
python scripts/build_stgr.py package

# 6. Verify the result
python scripts/smoke_test.py --binary firefox/obj-*/dist/bin/firefox.exe
python scripts/privacy_test.py --binary firefox/obj-*/dist/bin/firefox.exe
```

## mozconfig

`stgr/build/mozconfig.windows-x64-release` is the single release
configuration: release mode, `-O2` + LTO, sccache, NSIS installer, tests
disabled, and `--with-branding` pointing at the in-tree staged STGR branding
directory (`firefox/browser/branding/stgr`). The repository source remains in
`stgr/build/branding` and is copied during `build_stgr.py prepare`.

Point `MOZCONFIG` at it (or let `build_stgr.py` do it):

```bash
export MOZCONFIG="$(pwd)/stgr/build/mozconfig.windows-x64-release"
```

## First build time

A cold Firefox build takes **1–4+ hours** on typical hardware and much longer
on constrained CI runners. sccache + the CI caches (`.github/workflows/ci.yml`)
cut rebuilds drastically. Don't be alarmed by the first build — it is the
expensive one.

## CI/CD (single workflow)

`.github/workflows/ci.yml` is the entire pipeline: on every push to `main` it
bumps the patch version (`scripts/next_version.py`), builds the browser,
packages the installer + portable archive, creates tag `vX.Y.Z` and publishes
a GitHub Release with the `.exe`. No tag push or separate release workflow is
needed — see `docs/release-process.md`.

## Local iteration

```bash
cd firefox
python mach build          # incremental rebuild
python mach run            # run the built browser with a scratch profile
python mach package        # repackage after changes
```

## Troubleshooting

- **bootstrap fails on network** — run it again; it resumes.
- **Patch fails to apply** — do not force it: `scripts/apply_patches.py check`
  tells you which file drifted; rebase the patch by hand.
- **Windows Defender/SmartScreen** — unsigned local builds trigger warnings;
  that is expected. See `docs/release-process.md` for signing.
