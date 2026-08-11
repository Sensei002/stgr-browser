# STGR Updater

The updater ships updates from the official **GitHub Releases** source — no
custom update infrastructure for v1 (per spec §34).

## Components

| Piece | Location | Role |
|---|---|---|
| In-browser module | `browser/components/stgr/updater/STGRUpdater.sys.mjs` (patch 0006) | `check()` queries the release API; `verify()` validates SHA256 before any use |
| CLI tool | `scripts/check_update.py` | Same validation contract, usable by users and CI |
| Release source | `STGR_UPDATE_REPOSITORY` (stgr-config.json → `product.update_repository`) | Configurable — never hard-coded to a personal repo |
| Settings UI | About page → "Check for updates" | Phase 9 wiring: preferences pane |

## Validation contract (§35)

Every update candidate must pass **all** of:

1. **HTTPS** transport only.
2. **Product** — asset must be `STGR-Browser-…`.
3. **Version** — strictly newer than installed; **downgrades rejected**.
4. **Architecture** — `-Win64-Setup.exe` on Windows x64.
5. **SHA256** — must match the published `SHA256SUMS.txt`.
6. **Signature** — validated when a signing certificate is published.
7. **Unknown release** — malformed tags/pre-releases rejected.

Rejected: corrupt packages, wrong architecture, downgrades, bad hashes, bad
signatures, unknown releases. The updater **never executes** downloaded files
automatically — the user chooses to run the installer.

## Privacy

The updater performs **no** background network activity. Checks happen only
when the user clicks "Check for updates" (interval pref `stgr.updateCheck.
interval` is a hint for the future preferences pane, not a background poller).
