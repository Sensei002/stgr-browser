# STGR Browser Update System

## Architecture

STGR Browser uses a custom update server for distributing browser updates. The system supports automatic background updates, delta updates, and rollback.

## Update Server

### Server Endpoint

```
https://updates.stgr-browser.dev/
```

### API

#### Check for Updates

```
GET /v1/update?product=STGR&version=1.0.0&build=20260701&platform=win64&channel=release
```

Response:
```json
{
  "update": {
    "available": true,
    "version": "1.0.1",
    "build": "20260715",
    "url": "https://updates.stgr-browser.dev/v1/download/1.0.1/stgr-browser-1.0.1-win64.exe",
    "hash": "sha256:abcdef...",
    "signature": "...",
    "size": 52428800,
    "releaseNotes": "https://stgr-browser.dev/releases/1.0.1",
    "timestamp": "2026-07-15T00:00:00Z"
  }
}
```

#### Download Update

```
GET /v1/download/{version}/{platform}/stgr-browser-{version}-{platform}.{ext}
```

#### Download Manifest (for delta updates)

```
GET /v1/manifest/{fromVersion}/{toVersion}/{platform}.json
```

### Update Types

| Type | Description | Size | Bandwidth |
|------|-------------|------|-----------|
| Full | Complete browser installer | ~50-80 MB | Highest |
| Partial | Binary diff (bsdiff) | ~10-30 MB | Medium |
| Complete Fallback | Full download if delta fails | ~50-80 MB | Highest |

### Channels

| Channel | Frequency | Quality | Default |
|---------|-----------|---------|---------|
| Release | Monthly | Highest | ✅ |
| Beta | Bi-weekly | Medium | ❌ |
| Nightly | Daily | Lower | ❌ |

## Client Implementation

### Update Check Flow

```
1. Browser starts
2. After 5s delay (startup optimization)
3. Check if update check is due (>24h since last check)
4. Send update check request to server
5. If update available:
   a. Download update in background (staging)
   b. Verify digital signature
   c. Stage update on disk
   d. Prompt user to restart
6. On restart, apply staged update
7. On success, launch new version
8. On failure, rollback to previous version
```

### Update Preferences

| Preference | Default | Description |
|-----------|---------|-------------|
| `app.update.auto` | true | Automatic download and apply |
| `app.update.enabled` | true | Enable update checking |
| `app.update.interval` | 86400000 | Check interval (24 hours) |
| `app.update.channel` | release | Update channel |
| `app.update.staging.enabled` | true | Stage updates before applying |
| `app.update.rollback.enabled` | true | Allow rollback on failure |

## Security

### Digital Signatures

- All updates are digitally signed using Ed25519
- Public key is embedded in the browser
- Signature is verified before staging
- If signature verification fails, update is rejected

### Verification Process

```bash
# Verify update package
openssl dgst -sha256 -verify stgr-public-key.pem \
  -signature update.sig update.exe
```

### Rollback

- Previous version is preserved during update
- If new version fails to start 3 times, automatic rollback
- Manual rollback via `about:stgr` → Troubleshooting → Rollback

## Implementation Plan

### Required Files

```
gecko-dev/browser/components/stgr-updater/
├── StgrUpdateService.jsm    # Main update service
├── StgrUpdateVerifier.jsm   # Signature verification
├── StgrUpdateStager.jsm     # Update staging and application
├── moz.build                # Build registration
├── content/
│   └── update-settings.js   # Update UI
└── locales/
    └── en-US/
        └── updater.ftl      # Localization strings
```

### Update Server (Separate Repository)

```
github.com/stgr-browser/update-server/
├── server.js                # Express.js server
├── manifest.json            # Available versions
├── releases/                # Update packages
└── keys/                    # Signing keys
```

### Key Management

- **Signing key**: Offline, air-gapped
- **Verification key**: Embedded in browser binary
- **Key rotation**: Supported via update manifests
