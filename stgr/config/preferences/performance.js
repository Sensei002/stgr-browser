// ─────────────────────────────────────────────────────────────
// STGR Browser — performance preference layer
// Canonical source of the block injected into browser/app/profile/firefox.js
// by patches/0004-stgr-gaming-mode.patch (keep in sync).
//
// Marker: BEGIN STGR PERFORMANCE PREFS / END STGR PERFORMANCE PREFS
//
// These are the STGR performance defaults and the memory-profile
// presets consumed by stgr/gaming-mode (patches/0004).
// Security-sensitive prefs (sandbox, isolation, mitigations) are
// intentionally NOT touched.
// ─────────────────────────────────────────────────────────────
// BEGIN STGR PERFORMANCE PREFS

// ---- Default performance posture -----------------------------------
// Hardware acceleration stays ON (never disabled by default).
pref("layers.acceleration.force-enabled", true);   // hardware acceleration
pref("gfx.webrender.all", true);                   // WebRender default path
// Reduce idle background activity.
pref("network.http.throttle.enable", true);
pref("browser.sessionstore.interval", 30000);      // session writes less chatty
pref("browser.tabs.unloadOnLowMemory", true);      // memory-pressure unloading

// ---- Memory profiles --------------------------------------------------
// normal:    stock Firefox behavior
// balanced:  moderate background-tab suspension and timer throttling
// aggressive: maximum background resource reduction (active tab protected)

pref("stgr.memoryProfile.normal.tabs.suspendAfterSeconds", 0);
pref("stgr.memoryProfile.balanced.tabs.suspendAfterSeconds", 600);
pref("stgr.memoryProfile.aggressive.tabs.suspendAfterSeconds", 120);
pref("stgr.memoryProfile.aggressive.timerThrottling", true);
pref("stgr.memoryProfile.aggressive.backgroundNetwork", false);
pref("stgr.memoryProfile.aggressive.animation", false);
pref("stgr.memoryProfile.aggressive.preload", false);

// ---- Gaming Mode preset (applied when stgr.gamingMode.enabled) --------
pref("stgr.gamingMode.suspendBackgroundTabs", true);
pref("stgr.gamingMode.reduceTimers", true);
pref("stgr.gamingMode.reduceNetwork", true);
pref("stgr.gamingMode.reduceAnimations", true);
pref("stgr.gamingMode.pausePreload", true);
// Protected media (audio/video/calls) and downloads are NEVER unloaded:
pref("stgr.gamingMode.protect.audio", true);
pref("stgr.gamingMode.protect.video", true);
pref("stgr.gamingMode.protect.downloads", true);
pref("stgr.gamingMode.protect.webrtc", true);

// END STGR PERFORMANCE PREFS
