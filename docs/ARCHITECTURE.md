# Architecture

## The one-paragraph version

STGR Browser is a **distribution** of upstream Chromium. We do not own the engine; we own
everything around it — identity, defaults, blocking rules, the new tab page, and the
installer. A build is a deterministic transformation: *pinned base + our layer → installer*.
Every input is a file in this repository, and every output is reproducible from a clean
checkout.

---

## Layers

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 4. Distribution layer      overrides/windows/installer.nsi               │
│                            shortcuts, protocol handler, policies, uninstall│
├──────────────────────────────────────────────────────────────────────────┤
│ 3. Identity layer          branding/brand.json + generate-icons.py        │
│                            icons (ico/icns/png), version resources, art   │
├──────────────────────────────────────────────────────────────────────────┤
│ 2. Behaviour layer         config/preferences  config/policies            │
│                            config/flags        config/blocklists          │
│                            extensions/  ntp/                              │
├──────────────────────────────────────────────────────────────────────────┤
│ 1. Engine layer            config/base.json -> pinned Chromium snapshot    │
│                            (upstream, unmodified except exe resources)     │
└──────────────────────────────────────────────────────────────────────────┘
```

Layers 2–4 are ours. Layer 1 is a third-party binary that we treat as read-only. If you ever
find yourself patching the engine in Stage 1, stop: that is Stage 2 work and needs a source
build.

---

## Build data flow

```
config/base.json ──┐
                   ├─> fetch_base()   download + sha256 verify + extract
config/base.lock.json ┘        │
                               ▼
                        build/base/chrome-win/
                               │  copytree (never mutate the source)
                               ▼
                        build/app/  ◄── assemble()
                               │        rename chrome.exe -> stgr.exe
                               │        rcedit: icon + version strings
                               │        write initial_preferences + master_preferences
                               │        copy extensions/{stgr-ntp,stgr-shield,stgr-theme}
                               │        compile STGRBrowser.exe (C# launcher)
                               │        write stgr-build.json (provenance)
                               ▼
branding/icons/stgr.ico ──> package() ──> dist/STGR-Browser-Setup-<v>-x64.exe
config/policies/base.json ─┘        │      dist/latest.json
overrides/windows/*.nsi             └────  dist/SHA256SUMS.txt
```

`build/app` is a complete, runnable browser directory. `--no-installer` stops there, which
is the fast QA path: you can launch `build/app/STGRBrowser.exe` directly.

---

## Runtime composition

When the user clicks the shortcut, this happens:

```
STGRBrowser.exe  (our C# launcher, 12 KB)
   │  builds the command line:
   │    <balanced flags from flags.conf>
   │    --user-data-dir=%LOCALAPPDATA%\STGR\Browser
   │    --load-extension=<app>\extensions\stgr-ntp,stgr-shield,stgr-theme
   │    <whatever the user passed through>
   ▼
stgr.exe  (renamed upstream Chromium)
   ├── reads initial_preferences      on first run only
   ├── reads HKCU\...\Policies\Chromium   (written by the installer)
   ├── loads the three bundled extensions
   └── renders the NTP from extensions/stgr-ntp
```

Why a launcher instead of putting switches on the shortcut: a browser is launched from many
places — shortcut, `stgr://` handler, taskbar jump list, another app's "open with". One
binary owning the flag set means the flags can never drift between entry points.

---

## The three bundled extensions

| Extension | Type | Responsibility | Why an extension and not code |
|---|---|---|---|
| `stgr-ntp` | MV3, `chrome_url_overrides.newtab` | New Tab Page: speed dial, search, link rail | The NTP is web content. Overriding it needs no engine change, and the page can be iterated without a rebuild. |
| `stgr-shield` | MV3, `declarative_net_request` | Ad/tracker blocking | DNR rules are evaluated in the network stack before a socket opens. Zero JS per request, which is the whole point on a low-memory browser. |
| `stgr-theme` | MV3 `theme` key | Tab strip / toolbar / frame colours | The only supported way to recolour Chromium chrome without a source build. |

All three are loaded with `--load-extension`, which keeps them out of the profile and means
a browser update cannot leave a stale copy behind. User-installed extensions from the Chrome
Web Store work normally alongside them.

---

## What is *not* ours (and why that is fine)

The tab strip, the toolbar, the omnibox, the sidebar, and the settings page are upstream
Chromium Views UI. In Stage 1 we can recolour them and that is all. Everything about their
layout — a custom sidebar, a custom toolbar button set, the mockup's exact geometry — requires
editing `chrome/browser/ui/views/` and rebuilding the engine.

That is exactly what `patches/` and [ROADMAP.md](ROADMAP.md) are for. Do not attempt to
fake it with CSS in the NTP; the NTP only owns the content area.

---

## Failure domains

Knowing which failure is contained by what saves a lot of time:

| Failure | Blast radius | Detection |
|---|---|---|
| `brand.json` missing a key | Every generator | `scripts/check-brand.py` in CI |
| Icon pipeline broken | Installer icon, taskbar icon, NTP hero | CI asserts ICO/ICNS structure |
| Flagset typo | Browser launches but behaves oddly — no error | `--print-flags` review; manual QA |
| `initial_preferences` malformed | Prefs silently ignored, browser uses Chromium defaults | Manual: fresh profile + `chrome://prefs-internals` |
| DNR ruleset invalid | Extension fails to load, **no blocking at all** | CI validates rule shape |
| NSIS syntax error | No installer | CI `installer-dryrun` job |
| Base download drift | Different engine revision per build | `base.lock.json` + sha256 check |

The two silent ones are the flagset and `initial_preferences`. Both are configuration, not
code, so nothing type-checks them. When behaviour looks wrong but nothing errors, suspect
those first.
