# Third-Party Components

STGR is built on Mozilla Firefox, which itself contains hundreds of
third-party components. This inventory is maintained alongside
`THIRD_PARTY_NOTICES.md`; the authoritative license texts live in the Firefox
source (`LICENSE`, `toolkit/content/license.html`, `third_party/`) and are
reachable in the browser via `about:license`.

## Bundled software

| Name | Version | License | Source | Modifications |
|---|---|---|---|---|
| Mozilla Firefox / Gecko / SpiderMonkey | pinned in `stgr-config.json` (`firefox.upstream_version`) | MPL-2.0 | github.com/mozilla-firefox/firefox | STGR patch series only; no upstream notices removed |
| uBlock Origin | pinned in `stgr-config.json` (`ublock.version`) | GPL-3.0 | github.com/gorhill/uBlock | **None** — official signed XPI bundled unmodified; attribution preserved |
| Other Firefox components (libvpx, libwebp, SQLite, ICU, zlib, Brotli, NSS, NSPR, cairo, …) | per upstream | per upstream | Firefox source | None |

## Tooling (not shipped in the browser)

| Tool | License |
|---|---|
| MozillaBuild | MPL-2.0 |
| Rust / Cargo | MIT / Apache-2.0 |
| Visual Studio Build Tools | Microsoft (proprietary; not redistributed) |
| Windows SDK | Microsoft (proprietary; not redistributed) |
| sccache | Apache-2.0 |
| Pillow (icon tooling) | HPND |
| psutil (optional) | BSD-3-Clause |

## Compliance rules

1. Preserve every upstream copyright and license notice.
2. uBlock Origin: GPL-3.0 obligations — the license text ships with the
   extension and the corresponding unmodified source is linked from
   `stgr/extensions/ublock-origin/README.md`.
3. Do not falsely claim STGR created uBlock Origin or any third-party
   component.
4. Do not distribute proprietary Mozilla assets.
5. When bundling anything new, add it to this table + `THIRD_PARTY_NOTICES.md`
   and open a `documentation` issue for review.

## If you spot a missing notice

Open an issue (label `documentation`) — we are committed to full compliance.
