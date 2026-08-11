# Security Policy — STGR Browser

## Supported versions

| Version | Supported |
|---|---|
| Latest stable release | ✅ |
| Previous stable release | ✅ (until the next release ships) |
| Nightly/Beta (when they exist) | ⚠️ best-effort |

STGR tracks **Mozilla Firefox Stable**. Firefox security updates are high priority: when Mozilla
publishes a stable security release, STGR rebuilds against it as soon as the rebase and tests pass.
Security-driven updates are clearly marked `SECURITY UPDATE` in the automation.

## Security principles

STGR **never** weakens Firefox's security model — not for benchmarks, not for RAM numbers, not for
startup time:

- Gecko security model remains intact.
- Firefox sandboxing remains intact.
- Site/process isolation remains intact.
- HTTPS / certificate validation remains intact.
- Extension security remains intact (signed extensions required, as upstream).
- Update verification remains intact (HTTPS + version/arch/hash/signature validation).
- No disabling of memory-safety protections or anti-exploitation mitigations.

Any proposed change that touches these areas must be documented with a security review, even for
configuration changes. See [`docs/privacy.md`](docs/privacy.md) for the network/privacy posture.

## Reporting a vulnerability

**Do not open a public issue for security vulnerabilities.**

1. **Private disclosure:** email the maintainers at `security@steigerdojo.example`
   (replace with the real address in your fork) with subject `[STGR Security] ...`.
2. Include: affected version(s), Firefox base version, a minimal reproduction, impact, and (if
   known) a suggested fix. Do not include exploit code in the first message.
3. You will receive an acknowledgement within **72 hours**. We will coordinate a fix, and credit
   you in the release notes unless you prefer otherwise.

Alternatively, for vulnerabilities that exist in upstream Firefox, report them directly to Mozilla's
[bug bounty program](https://www.mozilla.org/en-US/security/bug-bounty/) — STGR is built on the
same code and benefits from the same upstream fixes.

## Secrets

- Never commit `.pfx`, `.p12`, private keys, GitHub tokens, or any credentials — they are
  gitignored and CI fails on leaked secrets (`.github/workflows/security.yml` runs a secret scan).
- Code-signing certificates are stored in GitHub Secrets or a secure signing service, and are
  **never** exposed to pull-request builds.

## Security automation

`.github/workflows/security.yml` runs on every push/PR:

- Secret scanning (Gitleaks).
- Dependency updates (Dependabot).
- A check that no STGR patch touches security-critical subsystems without approval.
- Periodic policy review.
