# STGR Browser

> **Built on Firefox. Designed for gamers. Private by default. No ads. No STGR telemetry. No unnecessary bloat.**
>
> — **STEiGER Dojo**

STGR Browser is an open-source, privacy-focused, gaming-oriented **Firefox fork** based on the
**latest stable Mozilla Firefox** source. It is a genuine Gecko build — not an Electron app, not a
wrapper, not a custom frontend sitting on top of Firefox.

**Primary target platform:** Windows x64.

---

## What makes STGR different

| Principle | What it means in practice |
|---|---|
| 🔒 No STGR telemetry | STGR-specific code collects zero telemetry. Firefox telemetry is disabled by default where it can be safely disabled, and what remains is documented in [`docs/privacy.md`](docs/privacy.md). |
| 🚫 No advertisements | No ad injection, no sponsored content, no affiliate links, no shopping/coupon/crypto bloat. |
| 🛡️ Strong privacy defaults | Privacy-first preference layer, no forced account, no forced sync, no unnecessary cloud services. |
| 🎮 Gaming Mode | Reduces background tab/timer/network activity while you game. A resource-management feature — not a fake "FPS booster". |
| ⚡ Performance first | Low idle CPU/RAM, fast startup, smooth scrolling, measured — never benchmark-faked. |
| 🎨 Dojo aesthetic | Dark red + black, minimal, premium, Japanese-dojo inspired. Red is an accent, not a light show. |
| 🔌 Full WebExtensions | Full Firefox extension compatibility. uBlock Origin ships pre-installed and enabled by default. |
| 🔄 Tracks Firefox Stable | STGR is rebased onto every Firefox Stable release, with automated update tooling. |

## Repository layout

```
stgr-browser/
├── firefox/            ← Firefox upstream source (synced by scripts, NOT committed)
├── stgr/               ← The STGR overlay layer (branding, config, ui, privacy, performance, ...)
├── patches/            ← STGR patch series applied on top of the Firefox source
├── scripts/            ← Automation (update_firefox, apply_patches, build, benchmark, ...)
├── benchmark/          ← Benchmark harness config and baselines
├── docs/               ← Architecture, building, privacy, performance, releases, ...
├── automation/         ← Per-update working areas created by update_firefox.py
└── .github/workflows/  ← CI/CD (build, tests, release, firefox-update, security, performance)
```

Read [`docs/architecture.md`](docs/architecture.md) for the full picture.

## Quick start (Windows x64)

```bash
# 0. Install prerequisites (see docs/building.md):
#    MozillaBuild, Visual Studio Build Tools, Windows SDK (auto-detected by ./mach bootstrap)

# 1. Sync the Firefox stable source
python scripts/update_firefox.py sync

# 2. Apply the STGR patch series
python scripts/apply_patches.py apply

# 3. Bootstrap build tooling (first time only)
cd firefox && ./mach bootstrap

# 4. Configure and build (uses stgr/build/mozconfig.windows-x64-release)
python scripts/build_stgr.py build

# 5. Package installer + checksums
python scripts/build_stgr.py package
```

> Building Firefox from source is heavy: ~40 GB disk, 8 GB+ RAM, and a multi-hour build on the first
> run. CI performs the same steps in `.github/workflows/build-windows.yml`.

## Releases

Every stable release publishes to **GitHub Releases**:

- `STGR-Browser-<version>-Win64-Setup.exe` — installer
- `STGR-Browser-<version>-Win64.zip` — portable archive
- `SHA256SUMS.txt` — checksums
- `STGR-source-<version>.zip` — source snapshot

See [`docs/release-process.md`](docs/release-process.md).

## Documentation

| Document | Covers |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Source architecture, overlay layer, update model |
| [`docs/building.md`](docs/building.md) | Windows build prerequisites and commands |
| [`docs/firefox-updates.md`](docs/firefox-updates.md) | Firefox Stable tracking and rebasing |
| [`docs/privacy.md`](docs/privacy.md) | Telemetry audit and remaining network activity |
| [`docs/performance.md`](docs/performance.md) | Performance targets and benchmark harness |
| [`docs/gaming-mode.md`](docs/gaming-mode.md) | Gaming Mode design |
| [`docs/release-process.md`](docs/release-process.md) | Release pipeline and conditions |
| [`docs/branding.md`](docs/branding.md) | Logo, colors, brand assets |
| [`docs/third-party.md`](docs/third-party.md) | Third-party licenses and attribution |

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Security issues: see [`SECURITY.md`](SECURITY.md).

## License

STGR Browser source (this overlay repository) is licensed under the
[Mozilla Public License 2.0](LICENSE), matching Mozilla Firefox's license. The Firefox upstream
source and all third-party components retain their own licenses — see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`docs/third-party.md`](docs/third-party.md).

## Disclaimers

- STGR Browser is **not affiliated with or endorsed by Mozilla**. "Firefox" and "Mozilla" are
  trademarks of the Mozilla Foundation, used only to describe the upstream basis.
- STGR Browser is **not affiliated with uBlock Origin** or Raymond Hill. uBlock Origin is bundled
  unmodified, under its GPL-3.0 license, with full attribution.
- "STGR", the STGR pagoda/道場 logo, and "STEiGER Dojo" are the property of STEiGER Dojo.
