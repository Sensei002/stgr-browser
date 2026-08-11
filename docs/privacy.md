# STGR Privacy — Audit & Network Transparency

**Goal:** no STGR telemetry, and Firefox telemetry disabled by default wherever
it can be disabled without breaking security, crash safety, updates, or
essential diagnostics. Where it cannot safely be removed, this document says
so.

## STGR-specific code

Collects **zero** data. Never collected: history, URLs, search queries, usage
statistics, fingerprints (browser/hardware), advertising identifiers, browsing
behavior, extension usage, tab statistics, performance analytics, profiles.
No analytics SDKs, tracking pixels, behavioral analytics, or "anonymous"
analytics. The privacy test (`scripts/privacy_test.py`) fails CI if any
unexpected outbound host — especially any telemetry endpoint — is contacted.

## Firefox telemetry — disabled by default

Applied via `stgr/config/preferences/privacy.js` (compiled in by
`patches/0002`):

- Unified telemetry: `toolkit.telemetry.enabled/unified` = false; server
  cleared.
- All ping types: archive, BHR, first-shutdown, shutdown-sender,
  new-profile, update, pioneer availability, reporting policy.
- Data reporting / health report: `datareporting.policy.dataSubmissionEnabled`
  and `datareporting.healthreport.uploadEnabled` = false.
- Shield/studies: `app.shield.optoutstudies.enabled` and `experiments.*` = false.
- Activity Stream/new tab telemetry and PingCentre = false.
- First-run noise: `aboutwelcome` off, `homepage_override.mstone` = ignore.
- Address-bar sponsored suggestions and Pocket-style feeds = off (also an
  anti-bloat measure).

## Crash reporting

Local crash collection stays enabled (crash safety). **Uploads are opt-in
only**: `toolkit.crashreporter.submitReports` and tab-crash sendReport are
false. The Settings → STGR Browser → Diagnostics view shows local diagnostics
(Firefox/STGR versions, OS, GPU, hardware acceleration, memory, extensions)
and never uploads them automatically.

## Remaining legitimate background network activity

A stock STGR build may contact these hosts while idle; they are required for
security and core browser function, not telemetry:

| Host | Purpose | Keep | Notes |
|---|---|---|---|
| `aus5.mozilla.org` | Update checks (app.update) | ✅ | Required for updates; you can set `app.update.enabled=false` |
| `addons.mozilla.org` | Extension installs/updates | ✅ | Only when extensions are used |
| `blocklist.addons.mozilla.org` | Add-on blocklist (security) | ✅ | |
| `shavar.services.mozilla.com` | Safe Browsing blocklist updates | ✅ | Can be disabled via safe-browsing prefs, at a security cost |
| `firefox.settings.services.mozilla.com` | Remote settings (security configs, blocklists) | ✅ | |

Deliberately **absent**: telemetry.mozilla.org, incoming telemetry, Normandy
(studies are off), Pocket, sponsored content, STGR/STEiGER Dojo servers, any
proxy, and any STGR-identifying headers.

## No-tracking guarantees

- No silent redirects through STEiGER Dojo servers.
- No injected STGR headers or tracking identifiers.
- No forced account, no forced sync, no unnecessary cloud services.
- Default search engine is configurable (DuckDuckGo default); no affiliate
  links, no result manipulation.

## Keeping the audit honest

Firefox adds telemetry subsystems over time. When it does:

1. Update `stgr/config/preferences/privacy.js` (and the 0002 patch block).
2. Re-run `lint_prefs_sync.py` and `privacy_test.py` in CI.
3. Update this table. Releases require the privacy test to pass.
