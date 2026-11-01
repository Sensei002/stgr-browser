# Release

Releases are produced by pushing a tag. There is no manual upload step.

---

## Cut a release

```bash
# 1. pick the version (semver; the tag must match VERSION)
echo "0.2.0" > VERSION

# 2. sync generated files that embed the version
python scripts/gen-ntp-config.py

# 3. verify
python scripts/check-brand.py
python -m compileall -q scripts branding
node --check ntp/app.js

# 4. commit and tag
git add -A
git commit -m "release: 0.2.0"
git tag v0.2.0
git push origin main --tags
```

The `build-windows` workflow runs on the tag and, on success:

- publishes `STGR-Browser-Setup-0.2.0-x64.exe`
- publishes `latest.json` (version, sha256, size, notes URL)
- publishes `SHA256SUMS.txt`
- marks the release as latest

A manual run from the Actions tab produces the same artifacts but only uploads them as a
workflow artifact, unless you tick **publish**.

---

## Version rules

`VERSION` is a single line, semver, no `v` prefix. `STGR_VERSION` overrides it in CI and is
derived from the tag (`v0.2.0` → `0.2.0`).

| Change | Bump |
|---|---|
| Branding, docs, NTP polish | patch |
| New flags, new blocked list, new installer behaviour | minor |
| Engine base bump, profile format change, anything that resets user data | minor, plus a note in the release body |
| Stage 2 (compiled branding) | major |

The engine revision is independent of the product version and is recorded in
`build/app/stgr-build.json` inside every build. Two builds of `0.2.0` with different engine
revisions are *not* the same binary — which is why `base.lock.json` should be pinned before
tagging.

---

## Pre-release checklist

- [ ] `config/base.lock.json` is committed and current.
- [ ] `VERSION` and the tag agree.
- [ ] `python scripts/build.py --print-flags balanced` output reviewed — no stray switches.
- [ ] `config/policies/base.json` still matches `docs/PRIVACY.md`.
- [ ] Fresh-profile smoke test on a clean Windows VM:
      install → launch → NTP renders → search works → a site with ads is blocked →
      `chrome://policy` all `OK` → uninstall removes shortcuts.
- [ ] `docs/AGENT-STATE.md` updated.

---

## Code signing

Builds are currently **unsigned**. Consequences and mitigations:

- SmartScreen shows "Windows protected your PC" on first run. Users click *More info* →
  *Run anyway*.
- Some corporate environments will block the installer outright.
- The uninstall entry and shortcuts are unaffected.

To sign, add a step between *Build installer* and *Checksums*:

```yaml
- name: Sign installer
  if: env.SIGNING_CERT != ''
  shell: pwsh
  env:
    SIGNING_CERT: ${{ secrets.SIGNING_CERT_PFX_BASE64 }}
    SIGNING_PASS: ${{ secrets.SIGNING_CERT_PASSWORD }}
  run: |
    $pfx = "$env:RUNNER_TEMP\cert.pfx"
    [IO.File]::WriteAllBytes($pfx, [Convert]::FromBase64String($env:SIGNING_CERT))
    & "${env:ProgramFiles(x86)}\Windows Kits\10\bin\x64\signtool.exe" sign `
      /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `
      /f $pfx /p $env:SIGNING_PASS dist\*.exe
```

Sign the installer **and** `build/app/stgr.exe` + `build/app/STGRBrowser.exe` before
packaging, otherwise the extracted binaries remain untrusted. An EV certificate removes the
SmartScreen warning immediately; a standard OV certificate needs reputation to accumulate.

---

## Rollback

Releases are immutable once published, which is the point. To roll back:

```bash
gh release edit v0.2.0 --draft          # unpublish
gh release edit v0.1.0 --latest         # point "latest" back
```

Users who already installed `0.2.0` are not downgraded automatically — there is no updater
yet (see [ROADMAP](ROADMAP.md)). Announce it.

---

## What a release contains

```
STGR-Browser-Setup-<v>-x64.exe   NSIS installer, per-user, ~95-120 MB
latest.json                      version, sha256, size, notes URL
SHA256SUMS.txt                   sha256 of the installer
```

Inside the installer, the app directory contains the engine, the launcher, the three
extensions, `initial_preferences`, and `stgr-build.json` for provenance.
