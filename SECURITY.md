# Security policy

## Reporting a vulnerability

Open a [private security advisory](https://github.com/stgr-browser/stgr-browser/security/advisories/new).
Do not open a public issue for anything exploitable.

Please include: the version from `chrome://version`, reproduction steps, and whether the
issue is in STGR code or in the Chromium engine.

## Scope

| In scope | Out of scope |
|---|---|
| The build pipeline (supply chain, artefact integrity) | Chromium engine vulnerabilities — report those to the Chromium project |
| The bundled extensions (`stgr-shield`, `stgr-ntp`, `stgr-theme`) | Third-party extensions the user installs |
| The installer (privilege handling, registry writes) | Vulnerabilities in sites the user visits |
| Configuration that weakens a security boundary | The absence of a feature that was never promised |

## Known, accepted risks

These are deliberate and documented. Reporting them as findings is not useful.

1. **Unsigned binaries.** SmartScreen warns on first run. Signing is planned; see
   [docs/RELEASE.md](docs/RELEASE.md#code-signing).
2. **Safe Browsing URL lookups are disabled.** Phishing protection is local-blocklist only.
   Trade-off documented in [docs/PRIVACY.md](docs/PRIVACY.md#the-safe-browsing-trade-off).
3. **`lowmem` profile removes per-tab process isolation.** This is why it is opt-in behind a
   separate shortcut, not the default. See [ADR-0004](docs/decisions/ADR-0004-dual-flag-profiles.md).
4. **Component updates are disabled.** CRLSet and blocklist components do not auto-refresh;
   they refresh with each release. Consequence of `ComponentUpdatesEnabled=false`.
5. **The base engine is an unpinned-by-hash snapshot until `base.lock.json` is committed.**
   Builds are reproducible by revision but not yet by hash. See
   [docs/BUILD.md](docs/BUILD.md#1-fetch_base).

## Supply chain

- The engine comes only from the official Chromium snapshot bucket. No third-party Chromium
  builds are used.
- `base.lock.json` pins the archive sha256 once committed; a mismatch fails the build.
- Actions are pinned to major versions (`@v4`, `@v5`). For a production release pipeline,
  pin to commit SHAs.
- `rcedit` is downloaded at build time from its GitHub release. If that download fails, the
  build continues without resource stamping rather than failing — a deliberate availability
  trade-off, but it means a silent branding regression is possible. CI asserts the installer
  exists, not that the icon is embedded.
