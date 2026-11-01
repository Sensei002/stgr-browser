# ADR-0001 — Windows-only, per-user distribution

**Status:** accepted
**Date:** 2026-11-01

## Context

The browser needs an installer. The options were: NSIS `.exe`, WiX `.msi`, or a portable zip.
Separately, we had to choose between a machine-wide install (HKLM, needs UAC) and a per-user
install (HKCU, no prompt). And we had to decide whether to ship macOS and Linux now.

## Decision

Windows 10/11 x64 only. NSIS `.exe` installer. Per-user install into
`%LOCALAPPDATA%\Programs\STGR`, no administrator prompt. Policies are written to
`HKCU\Software\Policies\Chromium`.

## Reasoning

**Per-user over machine-wide.** A browser that needs UAC to install or update is a browser
that stops getting installed and updated. Per-user installs also avoid the classic failure
where an elevated installer writes HKLM policies that a non-elevated browser instance then
reads inconsistently. Chromium honours HKCU policies with the same precedence as HKLM for a
per-user install, so nothing is lost.

**NSIS over MSI.** NSIS is preinstalled on GitHub's Windows runners, produces a single
self-contained `.exe`, allows a custom wizard that matches the brand, and handles the
registry writes we need without an external authoring tool. MSI would add WiX, an extra
build dependency, and a transform/component model we do not need. If enterprise deployment
(`msiexec /qn`, Group Policy assignment) becomes a requirement, an MSI can be added
alongside — the app payload is identical.

**Windows only.** Cross-platform was scaffolded and then removed. Maintaining three
packaging paths with one maintainer produces three half-tested paths. The architecture does
not preclude it: `config/base.json` already lists the `Mac`, `Mac_Arm` and `Linux_x64`
snapshot buckets, and [BUILD.md](../BUILD.md#adding-another-platform-later) documents the
four branches to reintroduce.

## Consequences

- No code signing yet, so SmartScreen warns. Accepted for a pre-release.
- Uninstall preserves `%LOCALAPPDATA%\STGR\Browser` on purpose — bookmarks and passwords are
  user data, not install artefacts. Removing it is a manual step.
- macOS and Linux users are unsupported. If that changes, the launcher is the first thing to
  port: the C# WinExe becomes a `CFBundleExecutable` shell script on macOS and a `.sh` on
  Linux.
