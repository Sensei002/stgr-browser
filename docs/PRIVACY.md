# Privacy model

STGR Browser claims "no telemetry". This document defines exactly what that means, what it
does not mean, and how to verify the claim yourself.

The honest summary: **the browser does not report on you.** It still talks to the network —
every browser must — but only to resolve and fetch what you asked for.

---

## Three independent layers

Telemetry in Chromium is controlled by more than one mechanism, and each can fail
independently. We use all three so a single regression does not leak.

| Layer | File | Applies to | Survives |
|---|---|---|---|
| 1. Launch switches | `config/flags/flags.conf` | Every process, every launch | A profile reset |
| 2. Seeded preferences | `config/preferences/stgr-defaults.json` | New profiles only | Nothing — one-shot at first run |
| 3. Enterprise policy | `config/policies/base.json` → `HKCU\Software\Policies\Chromium` | Every profile, always | Profile deletion, pref tampering |

Layer 3 is the load-bearing one. Policies outrank user preferences in Chromium's precedence
chain, which means a user (or a stray extension) cannot quietly turn metrics back on.

### What each layer disables

**Metrics and crash reporting**
`MetricsReportingEnabled=false`, `UrlKeyedAnonymizedDataCollectionEnabled=false`,
`--disable-breakpad`, `--disable-crash-reporter`, `--metrics-recording-only`.

**Usage signals**
`UserFeedbackAllowed=false`, `SpellCheckServiceEnabled=false`, `SearchSuggestEnabled=false`,
`AlternateErrorPagesEnabled=false`.

**Identity**
`BrowserSignin=0`, `SyncDisabled=true`, `signin.allowed=false`, `--disable-sync`.
No Google account surface is reachable, and no sync keys are generated.

**Advertising surfaces**
Privacy Sandbox is disabled wholesale (`PrivacySandboxSettings4` off, all `privacy_sandbox.*`
prefs false). No Topics, no FLEDGE, no attribution reporting.

**Speculative networking**
`NetworkPredictionOptions=2`, `net.network_prediction_options=2` — no DNS prefetch, no TCP
preconnect, no page prerender. These are the calls that happen before you click, which is
precisely the kind of thing a privacy claim should cover.

**Variations / field trials**
`ChromeVariations=1` — critical fixes only. Chromium normally downloads a trial configuration
that can enable arbitrary features server-side. Restricting it also stabilises behaviour:
what you test is what ships.

---

## What still reaches the network

Being precise about this matters more than the marketing claim.

| Destination | When | Can it be disabled |
|---|---|---|
| Your DNS resolver | Every navigation | Yes — set DoH to a resolver you trust, or run a local resolver |
| The site you navigated to | By definition | No |
| OCSP / CRL responders | On certificate validation | Partially; Chromium caches and batches |
| Captive portal probe | When a network looks filtered | No (this is how Wi-Fi login works) |
| Your default search engine | When you search | Yes — change it in settings; DuckDuckGo is the default |
| Extension update checks | Periodically, for store extensions | Only by removing the extension |

**Component updates are disabled** (`ComponentUpdatesEnabled=false`,
`--disable-component-update`). The trade-off is real: the CRLSet and the Safe Browsing
lists go stale. We accept it because our blocking list is compiled into the binary and
refreshed with each release.

---

## The Safe Browsing trade-off

`--disable-client-side-phishing-detection` plus `SafeBrowsingProtectionLevel=1` means:

- **No URL is ever sent to Google for reputation checking.** This is the privacy win.
- **Phishing and malware protection is weaker.** Local blocklists catch known-bad domains;
  they do not catch a freshly registered phishing domain.

This is a conscious choice, documented here so nobody "fixes" it by accident. If a future
version adds a local heuristic model, it goes in `stgr-shield` and this section gets updated
in the same commit.

---

## Ad and tracker blocking

`stgr-shield` compiles filter lists into `declarativeNetRequest` static rules at build time.

- Rules are evaluated inside the network stack, **before a socket opens**. The request is
  never made, so there is nothing to leak.
- **No filter list is downloaded at runtime.** No list-server sees your IP, and blocking
  works offline.
- The extension has no `webRequest` permission and no content scripts. It cannot read page
  content and cannot see what you type.
- Blocked counts are rendered by Chromium's own badge mechanism. No per-request JavaScript,
  no logging, no local database of what you visited.

Permissions requested, and why:

| Permission | Why it is needed |
|---|---|
| `declarativeNetRequest` | Register and toggle rulesets |
| `storage` | Remember the on/off toggle |
| `host_permissions: <all_urls>` | A blocking rule must be able to match any URL. It is not used to read pages. |

---

## Verifying it yourself

Claims are cheap. These are the checks that actually prove something:

1. **Watch the sockets.** Launch with `--enable-logging=stderr --v=1` (the `debug` profile),
   open `chrome://net-export`, capture 60 s of idle browsing, and load the log in
   [netlog viewer](https://netlog-viewer.appspot.com/). Idle traffic should be empty apart
   from your own navigations.
2. **Check the policy actually applied.** `chrome://policy` must show every key from
   `config/policies/base.json` with status `OK`. Anything `Not set` means the installer did
   not write the registry key — usually because it ran as a different user.
3. **Check the switches actually applied.** `chrome://version` lists the full command line.
   Compare it against `python scripts/build.py --print-flags balanced`.
4. **Check the prefs.** `chrome://prefs-internals` after a fresh profile. If a key is
   missing, `initial_preferences` was not read — which happens on any profile that already
   existed.

If any of those four disagree with this document, the document is wrong and the code is
right. Fix the document in the same commit.

---

## What we deliberately do not do

- No account, no sign-in, no sync, no "profile" in the cloud sense.
- No usage analytics, no crash upload, no A/B testing framework.
- No remote configuration that can change behaviour after release.
- No first-run "help us improve" prompt, because there is nothing to opt into.
- No bundled search deal. DuckDuckGo is the default because it is a reasonable default, not
  because of a revenue share.
