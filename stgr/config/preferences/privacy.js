// ─────────────────────────────────────────────────────────────
// STGR Browser — privacy preference layer
// Canonical source of the block injected into browser/app/profile/firefox.js
// by patches/0002-stgr-privacy-defaults.patch (keep in sync).
//
// Marker: BEGIN STGR PRIVACY PREFS / END STGR PRIVACY PREFS
//
// Goal: NO STGR telemetry, and Firefox telemetry disabled by default
// wherever it can be disabled without breaking security, updates, or
// crash safety. See docs/privacy.md for the full audit.
// ─────────────────────────────────────────────────────────────
// BEGIN STGR PRIVACY PREFS

// ---- Unified telemetry master switches -------------------------
pref("toolkit.telemetry.enabled", false);
pref("toolkit.telemetry.unified", false);
pref("toolkit.telemetry.server", "");

// ---- Per-ping telemetry subsystems ------------------------------
pref("toolkit.telemetry.archive.enabled", false);
pref("toolkit.telemetry.bhrPing.enabled", false);
pref("toolkit.telemetry.firstShutdownPing.enabled", false);
pref("toolkit.telemetry.shutdownPingSender.enabled", false);
pref("toolkit.telemetry.newProfilePing.enabled", false);
pref("toolkit.telemetry.updatePing.enabled", false);
pref("toolkit.telemetry.pioneer-new-studies-available", false);
pref("toolkit.telemetry.reportingpolicy.firstRun", false);

// ---- Data reporting & health report ------------------------------
pref("datareporting.policy.dataSubmissionEnabled", false);
pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);
pref("datareporting.healthreport.uploadEnabled", false);

// ---- Shield / studies (no experiments in STGR) -------------------
pref("app.shield.optoutstudies.enabled", false);
pref("experiments.active", false);
pref("experiments.supported", false);

// ---- Activity Stream / new tab telemetry -------------------------
pref("browser.newtabpage.activity-stream.telemetry", false);
pref("browser.ping-centre.telemetry", false);

// ---- First-run / onboarding noise ---------------------------------
pref("browser.aboutwelcome.enabled", false);
pref("browser.startup.homepage_override.mstone", "ignore");

// ---- Crash reporting: local diagnostics only, opt-in upload -------
pref("toolkit.crashreporter.enabled", true);   // keep local crash collection
pref("toolkit.crashreporter.submitReports", false); // never auto-submit
pref("browser.tabs.crashReporting.sendReport", false);
pref("browser.crashReports.unsubmittedCheck.enabled", false);

// ---- Network privacy ------------------------------------------------
// Disable prefetch/predictor: reduces idle network activity.
pref("network.prefetch-next", false);
pref("network.predictor.enabled", false);
pref("network.dns.disablePrefetch", true);
// No sponsored suggestions in the address bar.
pref("browser.urlbar.quicksuggest.enabled", false);
pref("browser.urlbar.quicksuggest.sponsored", false);
pref("browser.urlbar.suggest.quicksuggest.sponsored", false);
// No sponsored/financial content in the new tab.
pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);
pref("browser.newtabpage.activity-stream.feeds.snippets", false);
pref("browser.newtabpage.activity-stream.feeds.discoverystream", false);
// No Mozilla ad tiles / sponsored content / weather widgets in the new tab.
pref("browser.newtabpage.activity-stream.unifiedAds.tiles.enabled", false);
pref("browser.newtabpage.activity-stream.unifiedAds.spocs.enabled", false);
pref("browser.newtabpage.activity-stream.showWeather", false);

// ---- Keep security services ON --------------------------------------
// Safe Browsing, certificate services and update checks remain enabled;
// they are legitimate security functionality, not telemetry.
// (browser.safebrowsing.*, browser.tabs.remote.*, app.update.* defaults are kept)

// END STGR PRIVACY PREFS
