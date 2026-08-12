# STGR Release Process

## Release cadence

STGR generally follows Firefox Stable releases. Security patch releases are
prioritized and marked `SECURITY UPDATE`.

## Pipeline (ci.yml — single workflow)

```
push to main
  → auto version bump (patch, past the highest vX.Y.Z tag)
  → sync → patch → build → package
  → sign installer (when certificate configured)
  → recompute SHA256SUMS.txt
  → push version-bump commit ([skip ci]) + create tag vX.Y.Z
  → publish GitHub Release with assets + notes
```

Every push to `main` triggers the full pipeline; the release tag and version
are derived automatically by `scripts/next_version.py`. Manual runs are
available via `workflow_dispatch`.

### Assets (every stable release)

- `STGR-Browser-<version>-Win64-Setup.exe` — installer
- `STGR-Browser-<version>-Win64.zip` — portable archive
- `SHA256SUMS.txt` — generated from the final artifacts (never hand-written)
- `STGR-source-<version>.zip` — source snapshot (added to the release)
- `build-manifest.json` — provenance (§72–73)

Release notes include: STGR version, Firefox base version, security updates,
performance changes, new features, bug fixes, extension changes, known issues.

## Release conditions (§81)

A release may only be published when **all** hold:

- [ ] Build succeeds
- [ ] Unit/smoke tests pass
- [ ] Privacy tests pass (no unexpected outbound hosts)
- [ ] Extension tests pass (incl. uBlock Origin)
- [ ] Installer tests pass (fresh/upgrade/uninstall/reinstall)
- [ ] Updater tests pass (incl. the invalid/downgrade/hash matrix)
- [ ] No unresolved Firefox patch conflicts
- [ ] Security checks pass
- [ ] Required artifacts exist + SHA256 generated

## Failure policy (§82)

If Firefox updates and STGR fails to build — **do not publish**. If privacy,
security, installer, uBlock, or patch tests fail — **do not publish**. The
previous stable release stays available.

## Rollback (§83)

`.stgr/state.json` keeps `LAST_KNOWN_GOOD_FIREFOX` / `LAST_KNOWN_GOOD_STGR`.
Rollback is a release-engineering decision; installed users are never
auto-downgraded.

## Code signing (§71)

- Architecture is in place (`ci.yml` signs when secrets exist).
- Certificate stored **only** in GitHub Secrets (`WINDOWS_SIGNING_CERT_BASE64`
  + `WINDOWS_SIGNING_CERT_PASSWORD`) or a secure signing service — never in
  Git; keep `.pfx`/`.p12`/`.key` out of the tree and history.
- Without a certificate, releases are unsigned and SHA256-published.
  Unsigned builds may trigger Windows SmartScreen warnings — documented for
  users in the release notes.

## Update security (§35)

The updater validates: HTTPS, product name, version (no downgrades),
architecture, SHA256 vs published checksums, signature when available; rejects
corrupt/wrong-arch/downgrade/bad-hash/bad-signature/unknown releases, and
never executes downloads automatically.
