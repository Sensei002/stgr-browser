# STGR Browser Privacy Documentation

## Privacy Promise

STGR Browser is designed with privacy as a **core requirement**, not an afterthought. We believe your browsing data belongs to you and only you.

### What STGR Browser NEVER does

| Activity | Status |
|----------|--------|
| Collects telemetry | ❌ Removed |
| Tracks browsing history | ❌ Never |
| Sends usage statistics | ❌ Removed |
| Displays sponsored content | ❌ Removed |
| Recommends content | ❌ Removed |
| Runs experiments/studies | ❌ Removed |
| Requires user account | ❌ Never |
| Uses cloud sync | ❌ Removed |
| Includes crypto features | ❌ Never |
| Includes ads | ❌ Never |
| Includes AI assistant | ❌ Never |
| Includes shopping features | ❌ Removed |
| Sends background metrics | ❌ Removed |
| Third-party analytics | ❌ Removed |
| Pocket integration | ❌ Removed |
| Firefox Sync | ❌ Removed |

### Data Collection Comparison

| Data Point | Firefox | STGR Browser |
|-----------|---------|-------------|
| Installation ID | ✅ Collected | ❌ Not collected |
| Usage statistics | ✅ Collected | ❌ Not collected |
| Crash reports | ✅ Optional | ❌ Not collected |
| Studies/Experiments | ✅ Optional | ❌ Not possible |
| Sponsored suggestions | ✅ Optional | ❌ Not possible |
| Pocket recommendations | ✅ Collected | ❌ Not collected |
| Shopping data | ✅ Optional | ❌ Not possible |
| Sync data | ✅ Optional | ❌ Not possible |

## Removed Components

### Telemetry Infrastructure (Patch 0001)

The following telemetry-related code is fully removed:

- `toolkit/components/telemetry/` - Core telemetry collection
- `toolkit/components/normandy/` - Studies/experiments system
- `toolkit/components/crashes/` - Crash reporting
- `browser/components/telemetry/` - Browser UI telemetry
- `devtools/` telemetry hooks

### Data Collection Services (Patch 0002)

- `browser/components/pocket/` - Pocket integration
- `services/sync/` - Firefox Sync
- `services/fxaccounts/` - Firefox Accounts

### Sponsored Content (Patch 0003)

- `browser/components/newtab/` - Sponsored top sites removed
- `browser/components/urlbar/` - Sponsored suggestions disabled
- `browser/components/shopping/` - Shopping removed
- `browser/components/asrouter/` - Messages/CFR disabled

## Privacy-Enhancing Defaults

STGR Browser ships with strict privacy defaults:

| Feature | Default | Description |
|---------|---------|-------------|
| Enhanced Tracking Protection | STRICT | Blocks trackers, fingerprinters, cryptominers |
| HTTPS-Only Mode | ON | Upgrades all connections to HTTPS |
| DNS-over-HTTPS | ON (Quad9) | Encrypted DNS queries |
| Third-Party Cookies | BLOCKED | Blocks cross-site tracking |
| Fingerprinting Protection | ON | Resist fingerprinting techniques |
| Query Parameter Stripping | ON | Removes tracking parameters |
| Network Partitioning | ON | Partitions all network state by site |
| Cookie Isolation | ON | First-party isolation by default |
| Autoplay | BLOCKED | Prevents unwanted media autoplay |
| Search Suggestions | OFF | No search query sent to provider |
| Safe Browsing | ON | Local protection, no data sent |
| Certificate Validation | STRICT | OCSP must-staple enforced |
| Mixed Content | BLOCKED | Blocks all mixed content |

## Network Requests

STGR Browser makes the following network requests:

### Required (for browser functionality)

1. **Update checks** (configurable)
   - `https://updates.stgr-browser.dev/update.json`
   - Periodic check for new versions
   - Can be disabled in settings

2. **Certificate revocation** (security)
   - OCSP requests to certificate authorities
   - Required for HTTPS certificate validation

3. **DNS**
   - DNS-over-HTTPS to Quad9 (configurable)
   - Can be changed or disabled

### Everything else is blocked

Any other network request from the browser itself (not from web pages) indicates a bug. Please report it.

## User Data

### What STGR Browser stores locally

| Data | Location | Purpose |
|------|----------|---------|
| Bookmarks | `places.sqlite` | User bookmarks |
| History | `places.sqlite` | Browsing history (can be cleared) |
| Passwords | `logins.json` | Saved passwords (encrypted) |
| Cookies | `cookies.sqlite` | Website cookies |
| Cache | `cache2/` | Website data (cleared periodically) |
| Extensions | `extensions/` | Installed extensions |
| Preferences | `prefs.js` | User settings |
| Session | `sessionstore.jsonlz4` | Open tabs (for restore) |

### All data is stored locally

- **No data is ever uploaded** to any server
- **No account** is required
- **No cloud** dependency
- **All data can be deleted** via Settings > Privacy & Security > Clear Data

## Verification

To verify STGR Browser's privacy behavior:

1. **Monitor network requests**:
   ```bash
   # Using Wireshark or similar
   # Filter for requests from stgr-browser.exe
   ```

2. **Check browser logs**:
   ```bash
   ./mach run -console
   ```

3. **Review source code**:
   All patches are in the `patches/` directory
   Every change is documented and verifiable

## Reporting Privacy Issues

If you find any unexpected data collection in STGR Browser:

1. **Open an issue** on GitHub
2. **Include**: Network log, steps to reproduce
3. **Severity**: Privacy issues are treated as critical

---

*Your privacy is not optional in STGR Browser. It is the foundation.*
