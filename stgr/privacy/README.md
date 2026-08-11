# STGR Privacy

This directory documents the privacy architecture. The enforcement lives in
`stgr/config/preferences/privacy.js` (compiled in by `patches/0002`), the
network posture is documented in `docs/privacy.md`, and the runtime privacy
gate is `scripts/privacy_test.py` (CI).

## Policy (STGR code)

- STGR-specific code collects **zero** data: no history, URLs, queries,
  fingerprints, hardware IDs, advertising IDs, usage stats, extension stats,
  tab stats, or profiles.
- No analytics SDKs, tracking pixels, behavioral analytics, or proprietary
  reporting — including "anonymous" analytics.
- The privacy test fails CI if any unexpected outbound host — especially any
  telemetry endpoint — is contacted.

## Policy (Firefox infrastructure)

- Firefox telemetry is disabled by default where it can be safely disabled
  (see the pref block). What remains (update checks, Safe Browsing, remote
  settings for security blocklists, add-on blocklisting) is legitimate
  security functionality and is documented in `docs/privacy.md`.
- Crash reporting stays **local by default**; upload is opt-in only.

## Audit trail

The canonical telemetry pref list lives in `stgr/config/preferences/privacy.js`.
When Firefox adds telemetry subsystems, the audit (docs/privacy.md) must be
updated and the corresponding prefs added — `lint_prefs_sync.py` keeps the
patch in sync, `privacy_test.py` keeps the network behavior honest.
