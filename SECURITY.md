# STGR Browser Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.x     | ✅ Active support  |
| < 1.0   | ❌ Pre-release     |

## Reporting a Vulnerability

STGR Browser takes security and privacy seriously. If you discover a security vulnerability, please report it responsibly.

### Do NOT file a public issue for security vulnerabilities.

Instead, send details to: **security@stgr-browser.dev**

### What to include

- **Description** of the vulnerability
- **Steps to reproduce** (proof of concept preferred)
- **Impact** — what an attacker could do
- **Affected versions**
- **Suggested fix** (if known)

### Response timeline

| Timeframe | Action |
|-----------|--------|
| 24 hours  | Acknowledgment of receipt |
| 7 days    | Initial assessment and priority |
| 30 days   | Patch release for critical issues |
| 90 days   | Public disclosure for resolved issues |

### Scope

We appreciate reports on:

- Remote code execution
- Sandbox escape
- Data exfiltration through browser APIs
- Privacy violations (unexpected data collection)
- Memory corruption
- URL/domain spoofing
- Extension security bypass

### Out of scope

- Missing SPF/DKIM DNS records (unless domain impersonation is demonstrated)
- Social engineering attacks requiring physical access
- Self-XSS
- Rate limiting on non-sensitive endpoints
- Theoretical attacks without practical exploitation

## Security Features

STGR Browser inherits Firefox's security architecture with STGR-specific hardening:

- **Sandboxing**: Content process sandbox at level 6 (maximum)
- **HTTPS-Only**: All connections upgraded by default
- **Certificate Pinning**: Strict enforcement
- **OCSP Must-Staple**: Required for certificate validation
- **Site Isolation**: Enabled by default
- **Process Isolation**: Separate processes for content, GPU, extensions
- **Memory Safety**: ASLR, DEP, CFG on Windows
- **Update Security**: Ed25519 signed updates with rollback

## Bug Bounty

STGR Browser does not currently offer a bug bounty program. Security researchers who report valid vulnerabilities will be credited in release notes and the CONTRIBUTORS file.

---

*STGR Browser is built on Mozilla Firefox's battle-tested security foundations, with all privacy-compromising features removed.*
