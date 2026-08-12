# STGR Build Configuration

| File | Purpose |
|---|---|
| `mozconfig.windows-x64-release` | The single Windows x64 release build configuration |
| `branding/` | Repository branding source staged into Firefox's in-tree `browser/branding/stgr` directory |
| `build-manifest.template.json` | Provenance template for `build-manifest.json` |

## Build invariants

1. **Supported optimizations only.** Release mode, `-O2`+ LTO, sccache. No
   experimental compiler flags "because benchmarks".
2. **No security regressions.** Sandbox, process isolation, certificate
   validation and all mitigations stay exactly as upstream. Nothing in this
   directory may weaken them.
3. **PGO is opt-in and honest.** `--enable-profile-guided-optimization` is
   commented out; enabling it requires a real representative workload
   (see `docs/performance.md`).
4. **One source of truth.** Everything here is driven by
   `stgr/config/stgr-config.json` through `scripts/build_stgr.py`.

## Reproducibility

Every packaged build records `build-manifest.json` (STGR version, Firefox
revision, commit, toolchain, patch list). A clean CI environment must be able
to reproduce the build from the manifest + the recorded revisions
(`.stgr/state.json` keeps the last-known-good revisions).
