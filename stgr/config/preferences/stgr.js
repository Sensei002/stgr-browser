// ─────────────────────────────────────────────────────────────
// STGR Browser — core preference layer
// Canonical source of the block injected into browser/app/profile/firefox.js
// by patches/0002-stgr-privacy-defaults.patch (keep in sync; lint_prefs_sync.py
// and build_stgr.py --verify-prefs-sync verify the markers below verbatim).
//
// Marker: BEGIN STGR PREFS / END STGR PREFS
// ─────────────────────────────────────────────────────────────
// BEGIN STGR PREFS

// ---- Branding & identity ------------------------------------
// Browser name is supplied by the branding directory; these prefs
// cover user-facing strings that are preference driven.
pref("app.update.channel", "stable");
pref("browser.aboutConfig.showWarning", true);

// ---- New Tab (lightweight STGR page) -------------------------
// Point the default new tab at the local STGR page (see 0003: the
// AboutNewTabRedirector honors this pref). Works fully offline; no
// Activity Stream telemetry is involved.
pref("browser.newtabpage.activity-stream.overrideURL",
     "resource://gre/res/stgr/newtab/newtab.html");
pref("browser.newtabpage.enabled", true);

// ---- Homepage -------------------------------------------------
pref("browser.startup.homepage", "resource://gre/res/stgr/newtab/newtab.html");

// ---- Search ----------------------------------------------------
// Configurable default; users can change it at any time.
pref("browser.search.defaultenginename", "DuckDuckGo");
pref("browser.search.order", 1);

// ---- STGR functional defaults ----------------------------------
// Gaming Mode: OFF by default. Values: off | on | automatic
pref("stgr.gamingMode.enabled", false);
pref("stgr.gamingMode.automatic", false);
// Memory profile: normal | balanced | aggressive
pref("stgr.memoryProfile", "balanced");
// STGR update check interval (seconds)
pref("stgr.updateCheck.interval", 604800);

// ---- Theme (dark dojo default) -----------------------------------
pref("extensions.activeThemeID", "firefox-compact-dark@mozilla.org");

// ---- Updater -------------------------------------------------------
pref("stgr.updateRepository", "Sensei002/stgr-browser");
pref("stgr.updateEnabled", true);

// END STGR PREFS
