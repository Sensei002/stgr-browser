# STGR Automation Scripts

Stdlib-only Python. No pip installs required for the core tooling (optional
`Pillow` for icon generation, `psutil` not required — Windows APIs are used).

| Script | Purpose |
|---|---|
| `common.py` | Shared config/state/run helpers (used by all scripts) |
| `_win.py` | Windows window/process/RAM/CPU helpers (ctypes) |
| `update_firefox.py` | Track Firefox Stable: `check` / `sync` / `update` / `report`. Writes `firefox-update-report.md`, maintains `.stgr/state.json` last-known-good revisions |
| `apply_patches.py` | `check` / `apply` / `status` for `patches/series`. Stops on conflict — conflicts are release-blocking |
| `build_stgr.py` | `prepare` (stage UI/branding/uBlock into the tree) · `build` · `package` (installer + SHA256SUMS + build-manifest.json) · `verify-prefs-sync` · `substitute` |
| `make_icons.py` | Generate the icon set + `stgr.ico` from `stgr/branding/stgr-logo.png` (needs Pillow); `--generate-placeholder` for pipeline testing |
| `fetch_ublock.py` | Download the official Mozilla-signed uBlock Origin XPI; records/verifies SHA256 (supply-chain tripwire) |
| `check_update.py` | CLI updater — validates product/version/arch/hash against GitHub Releases; `--download` fetches the installer. Exit codes feed CI |
| `smoke_test.py` | Launch → branding in title → tabs → settings → profile persistence across restart |
| `privacy_test.py` | Capturing-proxy network test: flags any unexpected outbound host or telemetry endpoint |
| `generate_checksums.py` | Write `SHA256SUMS.txt` for a directory of artifacts |
| `benchmark/benchmark.py` | Startup / idle RAM+CPU / 5·10·20-tab RAM; `--compare` runs regression thresholds |

## Golden command sequence

```bash
# 1. Sync + rebase onto the latest Firefox Stable
python scripts/update_firefox.py sync
python scripts/apply_patches.py check          # must be green
python scripts/apply_patches.py apply

# 2. Build (first time: bootstrap tooling first, see docs/building.md)
python scripts/build_stgr.py build
python scripts/build_stgr.py package

# 3. Verify
python scripts/smoke_test.py --json
python scripts/privacy_test.py --json
python scripts/benchmark/benchmark.py --runs 3

# 4. Release (CI does this automatically on tags)
python scripts/check_update.py --json
```

## Conventions

- Exit codes: `0` success · `1` error/failure · `2` update available (checkers).
- Everything reads `stgr/config/stgr-config.json` — never hard-code constants.
- No script performs network activity except when explicitly invoked (update
  check, uBlock fetch). The browser build must not depend on this repo's tooling
  at runtime.
