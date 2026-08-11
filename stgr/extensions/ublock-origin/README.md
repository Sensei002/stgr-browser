# uBlock Origin — pre-installed blocking

STGR ships the **official, Mozilla-signed uBlock Origin** XPI, unmodified.

## Source & verification

- Upstream: https://github.com/gorhill/uBlock (official stable releases)
- Version pinned in `stgr/config/stgr-config.json` → `ublock.version`
- The XPI is already signed by Mozilla's add-on signing service, so it
  installs through normal extension signature enforcement
  (`xpinstall.signatures.required` stays **on**).

`python scripts/fetch_ublock.py fetch` downloads
`uBlock0_<version>.firefox.signed.xpi` from the upstream GitHub release and
records its SHA256 in `ublock.sha256`. `fetch_ublock.py check` verifies the
local file. The recorded hash is a **supply-chain tripwire**: CI re-fetches
and fails if the artifact ever differs from what was reviewed.

## How it is bundled

At build time (`scripts/build_stgr.py prepare`), the XPI is placed at

```
firefox/distribution/extensions/uBlock0@raymondhill.net.xpi
```

and a `distribution/policies.json` force-installs it:

```json
{
  "policies": {
    "ExtensionSettings": {
      "uBlock0@raymondhill.net": {
        "installation_mode": "force_installed",
        "install_url": "file:///distribution/extensions/uBlock0@raymondhill.net.xpi"
      }
    }
  }
}
```

This is the standard, documented Firefox mechanism (used by LibreWolf and
others) — no source patch, no signature weakening, no proprietary ecosystem.

## Behavior & blocking policy

- uBlock Origin is **enabled by default** (ad/tracker/malware-domain blocking
  with its default filter lists).
- Users can inspect, modify, and disable blocking entirely.
- STGR does **not** maintain hidden custom blocklists. Any additional STGR
  rules would live here, open and auditable — none are added in v1.

## License & attribution

uBlock Origin is **GPL-3.0**, © Raymond Hill and contributors. It is bundled
unmodified; its license text and copyright notice ship with the extension, and
the corresponding source is the upstream repository. STGR is not affiliated
with uBlock Origin or Raymond Hill. See `THIRD_PARTY_NOTICES.md`.
