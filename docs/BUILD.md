# Build

The build runs on GitHub Actions and nowhere else. This document explains each stage, what
it needs, and how to debug it when it breaks.

---

## Prerequisites (runner image)

`windows-latest` already provides everything:

| Tool | Used for | Provided by |
|---|---|---|
| Python 3.12 | every script | `actions/setup-python` |
| Pillow | icon + installer art generation | `pip install pillow` |
| NSIS 3 (`makensis`) | installer | preinstalled at `C:\Program Files (x86)\NSIS` |
| .NET Framework `csc.exe` | the launcher | preinstalled |
| `git`, `gh` | version + release | preinstalled |

`rcedit` is **not** preinstalled; `build.py` downloads it to `.cache/tools` and degrades
gracefully if that fails (the engine keeps upstream version resources — the build still
succeeds).

---

## Stages

### 1. `fetch_base()`

```
config/base.json  →  revision ("latest" → LAST_CHANGE)  →  chrome-win.zip
                 →  sha256 check against config/base.lock.json
                 →  extract to build/base/chrome-win/
```

The Chromium snapshot is ~250 MB compressed, ~600 MB extracted. A `.stamp` file records the
sha256 so re-extraction is skipped when the archive has not changed.

**Pinning.** With `revision: "latest"`, every build may pick a different engine. That is fine
for development and unacceptable for a release. To pin:

```bash
# 1. read the resolved revision and hash from the CI job summary, or:
STGR_UPDATE_LOCK=1 python scripts/build.py --no-installer   # on Windows only

# 2. commit config/base.lock.json
git add config/base.lock.json && git commit -m "build: pin chromium base"
```

Once the lock exists, a mismatch is a hard failure with an explicit message. That is
intentional: a silent engine change is the worst possible release bug.

### 2. `assemble()`

| Step | Detail |
|---|---|
| Copy | `build/base/chrome-win` → `build/app`. The base is never mutated. |
| Rename | `chrome.exe` → `stgr.exe`. Chromium resolves resources relative to the exe, so this is safe. |
| Stamp | `rcedit`: icon, `FileVersion`, `ProductName`, `CompanyName`, `LegalCopyright`. |
| Seed | `initial_preferences` + `master_preferences` from `config/preferences/stgr-defaults.json`. |
| Extensions | `ntp/`, `extensions/stgr-shield`, `extensions/stgr-theme` → `build/app/extensions/`. |
| Launcher | C# source → `csc /target:winexe` → `STGRBrowser.exe`. |
| Provenance | `build/app/stgr-build.json` with engine revision, flag counts, commit SHA. |

### 3. `package()`

`makensis` with ~14 `/D` defines:

```
/DVERSION /DVI_VERSION /DPRODUCT_NAME /DPRODUCT_SHORT /DPUBLISHER
/DPRODUCT_URL /DAPP_ID /DPROTOCOL /DSRCDIR /DOUTFILE /DICONFILE
/DPOLICYSCRIPT /DWIZARDIMAGE /DHEADERIMAGE
```

`config/policies/base.json` is converted to an NSIS `WriteRegStr`/`WriteRegDWORD` block at
build time (`build/policies.nsh`) and `!include`d into the installer section. Adding a policy
requires no NSIS edit — just a JSON key.

Output:

```
dist/STGR-Browser-Setup-<version>-x64.exe
dist/latest.json          machine-readable release descriptor
dist/SHA256SUMS.txt
```

---

## Timing

| Stage | Cold | Warm (base cached) |
|---|---|---|
| Download + extract base | 3–6 min | 0 |
| Assemble | < 10 s | < 10 s |
| NSIS compress (solid LZMA) | 8–12 min | 8–12 min |
| Total | ~15–20 min | ~10–13 min |

The cache key is `chromium-win64-<hash of base.lock.json>`. Without a lock file the key is
constant, so the cache still works — it just may hold a stale revision, which the sha256
check will reject and re-download.

---

## Running pieces locally

You cannot produce an installer locally (no NSIS, and R4 in AGENTS.md forbids it). You can:

```bash
python scripts/build.py --print-flags balanced     # inspect the switch list
python -m py_compile scripts/build.py             # syntax
python scripts/check-brand.py                     # brand integrity
```

To dry-run the NSIS script on a machine that does have NSIS:

```bash
makensis /V2 /DVERSION=0.0.0 /DVI_VERSION=0.0.0.0 \
  /DSRCDIR=build/stub/src /DOUTFILE=build/stub/out/stub.exe \
  overrides/windows/installer.nsi
```

CI does exactly this in the `installer-dryrun` job with a one-file stub payload.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `engine binary missing: ...\chrome.exe` | Snapshot layout changed, or extraction was partial | Delete `build/base` and `.cache/base`, rebuild |
| `sha256 mismatch` | Upstream re-published the revision, or the lock is stale | Re-run with `STGR_UPDATE_LOCK=1`, review the diff, commit |
| `csc.exe not found` | Runner image changed | Add `actions/setup-dotnet` or pin `windows-2022` |
| Installer builds but is 3 MB | `SRCDIR` resolved to an empty directory | Check the `/DSRCDIR` value in the log; it must be `build\app` |
| Installer succeeds, browser will not start | Launcher compiled but engine renamed twice | `build/app` must contain exactly one of `stgr.exe` / `chrome.exe` |
| `makensis: command not found` | NSIS missing on runner | `choco install nsis -y` as a step |
| Job killed at 60 min | Solid LZMA on a large payload plus a cold cache | Raise `timeout-minutes`, or switch to non-solid `lzma` |
| Policies show `Not set` in `chrome://policy` | Installer ran elevated (HKLM) while the browser runs unelevated (HKCU) | Policies are per-user by design; do not "fix" this by moving to HKLM |

---

## Adding another platform later

The Stage 1 pipeline is deliberately Windows-shaped because that is the current target. To
add macOS or Linux you need to reintroduce, per platform:

1. A `platforms` entry in `config/base.json` (the snapshot buckets already exist: `Mac`,
   `Mac_Arm`, `Linux_x64`).
2. An assemble branch: `.app` bundle rewrite + `codesign --deep --sign -` for macOS;
   `.desktop` + AppImage/deb for Linux.
3. A packaging branch: `hdiutil` / `appimagetool` / `dpkg-deb`.
4. A launcher: the C# one is Windows-only. macOS needs a `CFBundleExecutable` shell script
   (note: the app bundle already expects `Contents/MacOS/stgr`), Linux needs a `.sh`.

An earlier revision of this repo had those branches; they were removed when the target was
narrowed to Windows. `git log -- scripts/build.py` has the shape if you need it back.
