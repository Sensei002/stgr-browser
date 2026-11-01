# STGR Shield

Network-level ad and tracker blocking for STGR Browser.

## How it works

`scripts/build-shield-rules.py` reads the hosts-format lists declared in
[`config/blocklists/sources.json`](../../config/blocklists/sources.json), de-duplicates the
domains, and emits `declarativeNetRequest` static rules:

```json
{
  "id": 1,
  "priority": 1,
  "action": { "type": "block" },
  "condition": { "urlFilter": "||doubleclick.net^", "isUrlFilterCaseSensitive": false }
}
```

The `||domain^` anchor matches the domain and any subdomain, and nothing that merely
contains the string. Rules are chunked at `maxRulesPerRuleset` (25 000) because Chromium caps
rules per ruleset; the chunking is declared in `manifest.json` under
`declarative_net_request.rule_resources`.

At runtime Chromium evaluates these inside the network stack, before a socket opens. A
blocked request never exists, so there is nothing to leak and nothing to clean up afterwards.

## What it does not do

- **No cosmetic filtering.** Blocked ad slots may leave an empty box rather than a reflowed
  page. This is the main reason a user might also install uBlock Origin Lite.
- **No scriptlets.** Anti-adblock walls that require script injection will not be defeated.
- **No per-origin allowlist.** The popup toggles the whole ruleset.

The reasoning is in [ADR-0003](../../docs/decisions/ADR-0003-ad-blocking-dnr.md).

## Permissions, and why

| Permission | Justification |
|---|---|
| `declarativeNetRequest` | Register and toggle rulesets |
| `storage` | Persist the on/off toggle |
| `host_permissions: <all_urls>` | A blocking rule must be able to match any URL. Not used to read page content. |

There is no `webRequest`, no content script, and no `tabs` permission. The extension cannot
observe what you browse.

## Editing the blocklist

```bash
# 1. add domains to config/blocklists/stgr-core.txt (hosts format)
# 2. recompile
python scripts/build-shield-rules.py --offline   # local lists only
python scripts/build-shield-rules.py             # also pulls remote lists

# 3. the generated files are committed
git add extensions/stgr-shield/rules/ extensions/stgr-shield/manifest.json
```

CI runs the same script and asserts that rule ids are unique and every filter is
domain-anchored.

## Size budget

| Source set | Domains | Ruleset size |
|---|---|---|
| `stgr-core` only (offline) | ~100 | ~12 KiB |
| `stgr-core` + StevenBlack unified | ~75 000 (capped) | ~4 MB |

The cap is `maxTotalRules` in `sources.json`. Rules beyond the cap are dropped from the tail
of the sorted list and reported as a warning — raise the cap only if you have measured the
memory cost of the larger matcher.
