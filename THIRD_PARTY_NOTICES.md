# Third-Party Notices — STGR Browser

STGR Browser is built on Mozilla Firefox and bundles third-party components. We preserve all
upstream copyright notices and licenses. A machine-readable inventory is maintained in
[`docs/third-party.md`](docs/third-party.md); the authoritative license texts live in the Firefox
source tree (`LICENSE`, `toolkit/content/license.html`, `third_party/`).

## Mozilla Firefox

- **Component:** Firefox / Gecko / SpiderMonkey (upstream basis)
- **Version:** latest stable (see `stgr/config/stgr-config.json` → `firefox.upstream_version`)
- **Source:** https://github.com/mozilla-firefox/firefox
- **License:** Mozilla Public License 2.0 (MPL-2.0) — see [`LICENSE`](LICENSE)
- **Modifications:** STGR applies a patch series from `patches/`. The overlay layer lives in
  `stgr/`. No upstream copyright notices are removed.
- **Attribution:** "Firefox" and "Mozilla" are trademarks of the Mozilla Foundation. STGR Browser
  is not affiliated with or endorsed by Mozilla.

## uBlock Origin

- **Component:** uBlock Origin (pre-installed content blocker)
- **Version:** official stable release pinned in `stgr/config/stgr-config.json`
- **Source:** https://github.com/gorhill/uBlock — **unmodified** upstream
- **License:** GNU General Public License v3.0 (GPL-3.0), © Raymond Hill and contributors
- **Modifications:** none. STGR does not modify, fork, or re-sign uBlock Origin.
- **Attribution:** Bundled per GPL-3.0 terms: the license text and copyright notice ship with the
  extension, and the corresponding source is available at the upstream repository above. See
  `stgr/extensions/ublock-origin/README.md`.
- **Distribution method:** the official signed XPI (signed by Mozilla's add-on signing service) is
  placed in the browser's `distribution/extensions/` directory so it is force-installed at first
  profile creation, without weakening extension signature enforcement.

## Other third-party components

Mozilla Firefox incorporates hundreds of third-party components (libvpx, libwebp, SQLite, ICU,
zlib, Brotli, NSS, NSPR, cairo, etc.). Their licenses are enumerated in the Firefox source
(`toolkit/content/license.html` and `third_party/`) and are included in any STGR distribution via
the standard Firefox `about:license` page.

## Build tooling

| Tool | License |
|---|---|
| MozillaBuild | MPL-2.0 (Mozilla) |
| Rust / Cargo | MIT/Apache-2.0 |
| Visual Studio Build Tools | Microsoft (proprietary, redistribution not required) |
| Windows SDK | Microsoft (proprietary) |
| sccache | Apache-2.0 |
| Pillow (icon generation) | HPND (MIT-compatible) |
| psutil (benchmark tooling, optional) | BSD-3-Clause |

## Reporting an attribution problem

If you believe an attribution or license notice is missing or incorrect, open an issue labeled
`documentation` or contact the maintainers. We are committed to full compliance with all applicable
licenses.
