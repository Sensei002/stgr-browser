// ============================================================================
// STGR Browser - Default Preferences
// ============================================================================
// This file defines the default configuration for STGR Browser.
// Based on Firefox preferences with STGR optimizations applied.
// ============================================================================

// ---------------------------------------------------------------------------
// BRANDING
// ---------------------------------------------------------------------------
pref("browser.chrome.errorReporter.enabled", false);
pref("browser.chrome.errorReporter.infoColumn.enabled", false);
pref("startup.homepage_override_url", "");
pref("browser.startup.homepage", "about:home");
pref("browser.startup.page", 1);
pref("browser.aboutwelcome.enabled", false);

// Disable onboarding tours
pref("browser.onboarding.enabled", false);
pref("browser.newtabpage.activity-stream.feeds.topsites", false);
pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);
pref("browser.newtabpage.activity-stream.feeds.snippets", false);
pref("browser.newtabpage.activity-stream.prerender", false);
pref("browser.newtabpage.activity-stream.showSponsored", false);
pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
pref("browser.newtabpage.activity-stream.default.sites", "");

// ---------------------------------------------------------------------------
// TELEMETRY & DATA COLLECTION - ALL DISABLED
// ---------------------------------------------------------------------------
pref("datareporting.healthreport.uploadEnabled", false);
pref("datareporting.policy.dataSubmissionEnabled", false);
pref("datareporting.sessions.current.clean", true);
pref("devtools.onboarding.telemetry.log", false);
pref("toolkit.telemetry.enabled", false);
pref("toolkit.telemetry.unified", false);
pref("toolkit.telemetry.server", "");
pref("toolkit.telemetry.archive.enabled", false);
pref("toolkit.telemetry.bhrPing.enabled", false);
pref("toolkit.telemetry.cachedClientID", "");
pref("toolkit.telemetry.firstShutdownPing.enabled", false);
pref("toolkit.telemetry.hybridContent.enabled", false);
pref("toolkit.telemetry.newProfilePing.enabled", false);
pref("toolkit.telemetry.reportingpolicy.firstRun", false);
pref("toolkit.telemetry.shutdownPingSender.enabled", false);
pref("toolkit.telemetry.updatePing.enabled", false);
pref("toolkit.telemetry.bhrPing.enabled", false);
pref("toolkit.telemetry.crashreporter.enabled", false);
pref("security.certerrors.mitm.auto_enable_enterprise_roots", false);
pref("security.certerrors.mitm.priming_enabled", false);
pref("browser.tabs.crashReporting.sendReport", false);
pref("browser.crashReports.unsubmittedCheck.enabled", false);
pref("browser.crashReports.unsubmittedCheck.autoSubmit", false);
pref("browser.sessionstore.resume_from_crash", true);

// ---------------------------------------------------------------------------
// POCKET - DISABLED
// ---------------------------------------------------------------------------
pref("extensions.pocket.enabled", false);
pref("extensions.pocket.api", "");
pref("extensions.pocket.oAuthConsumerKey", "");
pref("extensions.pocket.site", "");
pref("extensions.pocket.onSaveRecs", false);
pref("extensions.pocket.showHome", false);
pref("extensions.pocket.showTagged", false);
pref("extensions.pocket.loggedIn", false);
pref("extensions.pocket.suggestedTags", false);

// ---------------------------------------------------------------------------
// FIREFOX SYNC - DISABLED
// ---------------------------------------------------------------------------
pref("services.sync.username", "");
pref("services.sync.engine.addons", false);
pref("services.sync.engine.bookmarks", false);
pref("services.sync.engine.history", false);
pref("services.sync.engine.passwords", false);
pref("services.sync.engine.prefs", false);
pref("services.sync.engine.tabs", false);
pref("services.sync.engine.addresses", false);
pref("services.sync.engine.creditcards", false);
pref("identity.fxaccounts.enabled", false);
pref("identity.fxaccounts.auth.enabled", false);
pref("browser.tabs.firefox-view", false);
pref("browser.tabs.firefox-view-next", false);

// ---------------------------------------------------------------------------
// STUDIES & EXPERIMENTS - DISABLED
// ---------------------------------------------------------------------------
pref("app.normandy.enabled", false);
pref("app.normandy.api_url", "");
pref("app.shield.optoutstudies.enabled", false);
pref("browser.laterrun.enabled", false);
pref("browser.laterrun.bookkeeping.profileCreation", 0);
pref("experiments.enabled", false);
pref("experiments.supported", false);
pref("experiments.manifest.uri", "");
pref("extensions.webservice.discoverURL", "");
pref("network.allow-experiments", false);

// ---------------------------------------------------------------------------
// SPONSORED & RECOMMENDED CONTENT - DISABLED
// ---------------------------------------------------------------------------
pref("browser.newtabpage.activity-stream.showSponsored", false);
pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
pref("browser.shopping.experience2023.enabled", false);
pref("browser.shopping.experience2023.active", false);
pref("browser.search.suggest.enabled", false);
pref("browser.urlbar.quicksuggest.enabled", false);
pref("browser.urlbar.quicksuggest.dataCollection.enabled", false);
pref("browser.urlbar.quicksuggest.shouldShowOnboardingDialog", false);
pref("browser.urlbar.groupLabels.enabled", false);
pref("browser.urlbar.suggest.quicksuggest", false);
pref("browser.urlbar.suggest.quicksuggest.sponsored", false);
pref("browser.urlbar.suggest.quicksuggest.nonSponsored", false);
pref("browser.urlbar.richSuggestions", false);
pref("browser.urlbar.trending.requireSearchMode", false);
pref("browser.urlbar.addons.featureGate", false);
pref("browser.urlbar.mdn.featureGate", false);
pref("browser.urlbar.pocket.featureGate", false);
pref("browser.urlbar.weather.featureGate", false);
pref("browser.urlbar.yelp.featureGate", false);

// ---------------------------------------------------------------------------
// PRIVACY & TRACKING PROTECTION
// ---------------------------------------------------------------------------
pref("privacy.trackingprotection.enabled", true);
pref("privacy.trackingprotection.pbmode.enabled", true);
pref("privacy.trackingprotection.emailtracking.enabled", true);
pref("privacy.trackingprotection.fingerprinting.enabled", true);
pref("privacy.trackingprotection.cryptomining.enabled", true);
pref("privacy.trackingprotection.socialtracking.enabled", true);
pref("privacy.partition.network_state", true);
pref("privacy.partition.always_partition_third_party_non_cookie_storage", true);
pref("privacy.partition.always_partition_third_party_non_cookie_storage.pbmode", true);
pref("privacy.resistFingerprinting", true);
pref("privacy.resistFingerprinting.autoDeclineNoUserInputCanvasPrompts", true);
pref("privacy.resistFingerprinting.block_mozAddonManager", true);
pref("privacy.resistFingerprinting.exemptedDomains", "");
pref("privacy.firstparty.isolate", true);
pref("privacy.usercontext.about_newtab_segregation.enabled", true);
pref("privacy.query_stripping.enabled", true);
pref("privacy.query_stripping.onboarding.enabled", false);
pref("privacy.sanitize.sanitizeOnShutdown", true);
pref("privacy.clearOnShutdown.cache", true);
pref("privacy.clearOnShutdown.cookies", false);
pref("privacy.clearOnShutdown.downloads", true);
pref("privacy.clearOnShutdown.formdata", false);
pref("privacy.clearOnShutdown.history", false);
pref("privacy.clearOnShutdown.offlineApps", true);
pref("privacy.clearOnShutdown.sessions", true);
pref("privacy.clearOnShutdown.siteSettings", false);
pref("network.cookie.lifetimePolicy", 2);
pref("network.cookie.thirdparty.sessionOnly", true);
pref("network.cookie.thirdparty.nonsecureSessionOnly", true);
pref("dom.storage_access.auto_grants", false);
pref("dom.storage_access.auto_grants.delayed", false);
pref("dom.storage_access.enabled", false);
pref("browser.contentblocking.category", "strict");

// ---------------------------------------------------------------------------
// SECURITY
// ---------------------------------------------------------------------------
pref("dom.security.https_only_mode", true);
pref("dom.security.https_only_mode_ever_enabled", true);
pref("dom.security.https_only_mode_pbm", true);
pref("security.ssl.enable_ocsp_stapling", true);
pref("security.ssl.enable_ocsp_must_staple", true);
pref("security.ssl.treat_unsafe_negotiation_as_broken", true);
pref("security.cert_pinning.enforcement_level", 2);
pref("security.mixed_content.block_active_content", true);
pref("security.mixed_content.block_display_content", true);
pref("security.mixed_content.upgrade_display_content", true);
pref("security.mixed_content.upgrade_display_content.image", true);
pref("security.sandbox.content.level", 6);
pref("security.sandbox.content.readPathWhitelist", "");
pref("security.sandbox.content.writePathWhitelist", "");
pref("security.fileuri.strict_origin_policy", true);
pref("security.xssfilter.enabled", true);
pref("browser.safebrowsing.enabled", true);
pref("browser.safebrowsing.malware.enabled", true);
pref("browser.safebrowsing.phishing.enabled", true);
pref("browser.safebrowsing.downloads.enabled", true);
pref("browser.safebrowsing.downloads.remote.enabled", false);
pref("browser.safebrowsing.downloads.remote.url", "");
pref("browser.safebrowsing.allowOverride", false);

// DNS
pref("network.trr.mode", 2);
pref("network.trr.uri", "https://dns.quad9.net/dns-query");
pref("network.trr.custom_uri", "https://dns.quad9.net/dns-query");
pref("network.trr.bootstrapAddr", "");
pref("network.trr.wait_for_portal", false);
pref("network.dns.disablePrefetch", false);
pref("network.dns.disablePrefetchFromHTTPS", false);

// ---------------------------------------------------------------------------
// MEMORY OPTIMIZATION
// ---------------------------------------------------------------------------
pref("browser.sessionhistory.max_entries", 50);
pref("browser.sessionhistory.contentViewerTimeout", 0);
pref("browser.sessionhistory.bfcacheIgnoreMemoryCost", false);
pref("browser.sessionrestore.defragment_count", 5);
pref("browser.sessionstore.interval", 60000);
pref("browser.sessionstore.max_tabs_undo", 10);
pref("browser.sessionstore.max_windows_undo", 3);
pref("browser.sessionstore.restore_on_demand", true);
pref("browser.sessionstore.restore_tabs_lazily", true);
pref("browser.sessionstore.restore_pinned_tabs_on_demand", true);
pref("browser.sessionstore.restore_flash", false);
pref("browser.pagethumbnails.capturing_disabled", true);
pref("browser.disable_autocomplete", true);
pref("browser.urlbar.autocomplete.enabled", true);
pref("browser.urlbar.maxRichResults", 6);
pref("browser.urlbar.suggest.history", true);
pref("browser.urlbar.suggest.bookmark", true);
pref("browser.urlbar.suggest.openpage", true);
pref("browser.urlbar.suggest.topsites", true);
pref("browser.urlbar.suggest.engines", true);
pref("browser.urlbar.dnsResolveSingleWordsAfterSearch", 0);
pref("browser.urlbar.quicksuggest.dataCollection.enabled", false);
pref("media.cache_size", 51200);
pref("media.cache_readahead_limit", 7200);
pref("media.cache_resume_threshold", 3600);
pref("media.hardware-video-decoding.enabled", true);
pref("media.navigator.mediadataretention", 0);
pref("media.memory_cache_max_size", 65536);
pref("media.memory_caches_combined_limit_kb", 256000);
pref("network.buffer.cache.size", 32768);
pref("network.http.max-connections", 64);
pref("network.http.max-persistent-connections-per-server", 8);
pref("network.http.max-persistent-connections-per-proxy", 16);
pref("network.http.max-connections-per-server", 10);
pref("network.http.pacing.requests.enabled", true);
pref("network.http.pacing.requests.burst", 8);
pref("network.http.pacing.requests.hz", 10);
pref("network.http.max-urgent-start-excessive-connections-per-host", 3);
pref("network.preload", true);
pref("network.http.speculative-parallel-limit", 6);
pref("gfx.canvas.accelerated", true);
pref("gfx.canvas.accelerated.cache-items", 1024);
pref("gfx.canvas.accelerated.cache-size", 512);
pref("gfx.content.azure.backends", "skia,direct2d1.1");
pref("gfx.webrender.all", true);
pref("gfx.webrender.enabled", true);
pref("gfx.webrender.quality.force-subpixel-aa-where-possible", true);
pref("gfx.webrender.compositor", true);
pref("gfx.webrender.compositor.force-enabled", true);
pref("gfx.webrender.precache-shared-blobs", true);
pref("image.mem.decode_bytes_at_a_time", 8192);
pref("image.mem.discardable", true);
pref("image.mem.shared", true);
pref("image.mem.surfacecache.max_size_kb", 204800);
pref("image.mem.surfacecache.min_expected_expire_ms", 60000);
pref("image.decode-immediately.enabled", true);
pref("layout.css.grid.enabled", true);
pref("layout.css.subgrid.enabled", true);
pref("javascript.options.mem.gc_compacting", true);
pref("javascript.options.mem.gc_incremental", true);
pref("javascript.options.mem.gc_incremental_slice_ms", 5);
pref("javascript.options.mem.gc_parallel_marking", true);
pref("javascript.options.mem.gc_parallel_compacting", true);
pref("javascript.options.mem.gc_always_tenure", true);
pref("javascript.options.mem.max", 256);
pref("javascript.options.mem.max_aux_contexts", 2);
pref("javascript.options.mem.nursery.max_kb", 16384);
pref("dom.disable_beforeunload", true);
pref("dom.ipc.processCount", 4);
pref("dom.ipc.processCount.extension", 1);
pref("dom.ipc.processCount.file", 1);
pref("dom.ipc.processCount.webLargeAllocation", 1);
pref("dom.ipc.processPrelaunch.enabled", false);
pref("dom.ipc.keepProcessesAlive.privilegedabout", 1);
pref("browser.tabs.unloadOnLowMemory", true);
pref("browser.tabs.unloadOnLowMemory.frecency.min", 100);
pref("browser.tabs.minInactiveDurationForUnload", 300000);

// Background tab sleeping
pref("browser.tabs.unloadOnLowMemory", true);
pref("browser.tabs.discard.enabled", true);

// ---------------------------------------------------------------------------
// GPU OPTIMIZATION
// ---------------------------------------------------------------------------
pref("gfx.webrender.quality.force-subpixel-aa-where-possible", true);
pref("gfx.webrender.compositor", true);
pref("gfx.webrender.compositor.force-enabled", true);
pref("gfx.webrender.all", true);
pref("gfx.webrender.enabled", true);
pref("gfx.webrender.allow-texture-cache-padding", false);
pref("gfx.webrender.max-dirty-rows", 64);
pref("gfx.webrender.picture-tile-width", 512);
pref("gfx.webrender.picture-tile-height", 512);
pref("gfx.webrender.split-triangles", true);
pref("gfx.webrender.upload-batch-size", 128);
pref("webgl.enable-webgl2", true);
pref("webgl.disable-angle", false);
pref("webgl.default-low-power", true);
pref("webgl.enable-draft-extensions", true);

// WebRender advanced compositing
pref("gfx.webrender.partial-present", true);
pref("gfx.webrender.allow-vrr", true);
pref("gfx.webrender.max-partial-present-valid-surface-age", 4);
pref("gfx.webrender.use-d3d12", true);
pref("gfx.process.thread-pool.enabled", true);

// ---------------------------------------------------------------------------
// CPU OPTIMIZATION
// ---------------------------------------------------------------------------
pref("dom.animations-api.autoremove.enabled", true);
pref("dom.animations-api.element-based.getAnimations.enabled", true);
pref("dom.animations-api.implicit-keyframes.enabled", true);
pref("dom.disable_beforeunload", true);
pref("dom.enable_performance", false);
pref("dom.enable_resource_timing", false);
pref("dom.enable_user_timing", false);
pref("dom.event.clipboard.eventsAllowed", false);
pref("layout.iframe.flattening", true);
pref("layout.css.supports-selector.enabled", true);
pref("layout.spv.enabled", false);
pref("network.http.pacing.requests.enabled", true);
pref("dom.workers.enabled", true);
pref("dom.workers.maxPerDomain", 8);

// ---------------------------------------------------------------------------
// UI OPTIMIZATION
// ---------------------------------------------------------------------------
pref("browser.ui.animation.enabled", true);
pref("browser.ui.animation.duration", 150);
pref("browser.tabs.allow_discard", true);
pref("browser.tabs.animate", true);
pref("browser.tabs.drawInTitlebar", true);
pref("browser.tabs.loadInBackground", false);
pref("browser.tabs.loadDivertedInBackground", false);
pref("browser.tabs.unloadOnLowMemory", true);
pref("browser.tabs.warnOnClose", false);
pref("browser.tabs.warnOnCloseOtherTabs", false);
pref("browser.tabs.warnOnOpen", false);
pref("browser.fullscreen.animate", false);
pref("browser.uidensity", 1);
pref("browser.compactmode.show", true);
pref("toolkit.cosmeticAnimations.enabled", true);
pref("browser.theme.dark-mode-toolbar", true);
pref("browser.theme.content-theme", 2);
pref("browser.theme.windows-native-theme", false);

// ---------------------------------------------------------------------------
// GAMING MODE
// ---------------------------------------------------------------------------
pref("stgr.gamingMode.enabled", false);
pref("stgr.gamingMode.threshold.foregroundProcess", "EXE:!game.exe,EXE:!eldenring.exe,EXE:!steam.exe,EXE:!battle.net.exe,EXE:!epicgameslauncher.exe,EXE:!valorant.exe,EXE:!csgo.exe,EXE:!dota2.exe,EXE:!lol.exe,EXE:!fortnite.exe,EXE:!minecraft.exe,EXE:!rocketleague.exe,EXE:!apexlegends.exe,EXE:!overwatch.exe,EXE:!destiny2.exe,EXE:!cod.exe,EXE:!gta5.exe,EXE:!r6.exe,EXE:!leagueclient.exe");

// Gaming mode performance prefs (applied when gaming mode is active)
pref("stgr.gamingMode.reduceBackgroundTabs", true);
pref("stgr.gamingMode.reduceTimers", true);
pref("stgr.gamingMode.reduceAnimations", true);
pref("stgr.gamingMode.optimizeGPUScheduling", true);
pref("stgr.gamingMode.limitInactiveTabs", true);
pref("stgr.gamingMode.reduceRAMUsage", true);
pref("stgr.gamingMode.prioritizeActiveTab", true);
pref("stgr.gamingMode.reduceNetworkPolling", true);

// Gaming mode specific overrides (applied on activation)
pref("stgr.gamingMode.dom.ipc.processCount", 2);
pref("stgr.gamingMode.dom.ipc.processCount.extension", 0);
pref("stgr.gamingMode.browser.sessionstore.interval", 120000);
pref("stgr.gamingMode.media.cache_size", 25600);
pref("stgr.gamingMode.image.mem.surfacecache.max_size_kb", 102400);
pref("stgr.gamingMode.javascript.options.mem.max", 128);
pref("stgr.gamingMode.network.http.max-connections", 32);

// ---------------------------------------------------------------------------
// EXTENSIONS
// ---------------------------------------------------------------------------
pref("extensions.enabledScopes", 15);
pref("extensions.autoDisableScopes", 15);
pref("extensions.allow-non-mpc-extensions", true);
pref("extensions.webextensions.remote", true);
pref("extensions.webextensions.restrictedDomains", "");
pref("xpinstall.whitelist.required", false);
pref("xpinstall.signatures.required", false);
pref("extensions.langpacks.signatures.required", false);
pref("extensions.manifestV2.enabled", true);
pref("extensions.manifestV3.enabled", true);

// ---------------------------------------------------------------------------
// NETWORK
// ---------------------------------------------------------------------------
pref("network.http.http2.enabled", true);
pref("network.http.http2.push", true);
pref("network.http.http2.priority", true);
pref("network.http.http3.enabled", true);
pref("network.http.http3.priortize_http3", true);
pref("network.http.http3.alt-svc-mapping-for-testing", "");
pref("network.dns.disablePrefetch", false);
pref("network.dns.disablePrefetchFromHTTPS", false);
pref("network.predictor.enabled", false);
pref("network.prefetch-next", true);
pref("network.preload", true);
pref("network.http.speculative-parallel-limit", 6);
pref("network.http.max-connections", 64);
pref("network.http.max-persistent-connections-per-server", 8);
pref("network.http.max-connections-per-server", 10);
pref("network.websocket.max-connections", 128);
pref("network.trr.mode", 2);
pref("network.trr.uri", "https://dns.quad9.net/dns-query");

// ---------------------------------------------------------------------------
// DOWNLOADS
// ---------------------------------------------------------------------------
pref("browser.download.autohideButton", false);
pref("browser.download.manager.addToRecentDocs", true);
pref("browser.download.manager.closeWhenDone", false);
pref("browser.download.manager.focusWhenStarting", true);
pref("browser.download.manager.retention", 2);
pref("browser.download.manager.showAlertOnComplete", true);
pref("browser.download.manager.showWhenStarting", true);
pref("browser.download.manager.scanWhenDone", true);
pref("browser.download.useDownloadDir", true);
pref("browser.download.viewableInternally.typeWasRegistered", true);

// ---------------------------------------------------------------------------
// MEDIA
// ---------------------------------------------------------------------------
pref("media.autoplay.default", 0);
pref("media.autoplay.blocking_policy", 0);
pref("media.autoplay.enabled", true);
pref("media.ffmpeg.vaapi.enabled", true);
pref("media.hardware-video-decoding.enabled", true);
pref("media.hardware-video-decoding.force-enabled", true);
pref("media.navigator.enabled", true);
pref("media.peerconnection.enabled", true);
pref("media.videocontrols.picture-in-picture.enabled", true);
pref("media.videocontrols.picture-in-picture.video-toggle.enabled", true);
pref("media.videocontrols.picture-in-picture.allow-multiple", true);
pref("media.webspeech.synth.enabled", false);
pref("media.webspeech.recognition.enable", false);

// ---------------------------------------------------------------------------
// PDF VIEWER
// ---------------------------------------------------------------------------
pref("pdfjs.enabled", true);
pref("pdfjs.disableWorker", false);
pref("pdfjs.disableRange", false);
pref("pdfjs.disableStream", false);
pref("pdfjs.disableAutoFetch", false);
pref("pdfjs.disableFontFace", false);
pref("pdfjs.annotationMode", 2);
pref("pdfjs.enableHighlight", true);
pref("pdfjs.enableHighlightFloatingButton", true);
pref("pdfjs.sidebarViewOnLoad", 0);
pref("pdfjs.scrollModeOnLoad", 0);
pref("pdfjs.spreadModeOnLoad", 0);

// ---------------------------------------------------------------------------
// READER MODE
// ---------------------------------------------------------------------------
pref("reader.parse-on-load.enabled", true);
pref("reader.color_scheme", "dark");
pref("reader.font_size", 5);
pref("reader.font_type", "sans-serif");
pref("reader.toolbar.vertical", true);

// ---------------------------------------------------------------------------
// SEARCH ENGINES
// ---------------------------------------------------------------------------
pref("browser.search.order.1", "Google");
pref("browser.search.order.2", "DuckDuckGo");
pref("browser.search.order.3", "Bing");
pref("browser.search.hiddenOneOffs", "");
pref("browser.search.suggest.enabled", false);
pref("browser.search.separatePrivateDefault", true);
pref("browser.search.separatePrivateDefault.ui.enabled", true);
pref("browser.urlbar.placeholderName", "DuckDuckGo");
pref("browser.urlbar.placeholderName.private", "DuckDuckGo");

// ---------------------------------------------------------------------------
// STARTUP OPTIMIZATION
// ---------------------------------------------------------------------------
pref("browser.startup.homepage", "about:home");
pref("browser.startup.page", 3);
pref("browser.startup.blankWindow", false);
pref("browser.sessionstore.restore_pinned_tabs_on_demand", true);
pref("browser.sessionstore.restore_tabs_lazily", true);
pref("browser.sessionstore.restore_on_demand", true);
pref("browser.sessionstore.max_resumed_crashes", 1);
pref("browser.sessionstore.restore_hidden_tabs", false);
pref("browser.cache.offline.enable", false);
pref("browser.cache.offline.storage.enable", false);

// ---------------------------------------------------------------------------
// AUTOMATIC UPDATES
// ---------------------------------------------------------------------------
pref("app.update.auto", true);
pref("app.update.enabled", true);
pref("app.update.interval", 86400000);
pref("app.update.background.scheduling.enabled", true);
pref("app.update.badge", true);
pref("app.update.badgeWaitTime", 86400000);
pref("app.update.checkInstallTime", true);
pref("app.update.download.backgroundInterval", 600);
pref("app.update.staging.enabled", true);
pref("app.update.url", "https://updates.stgr-browser.dev/update.json");
pref("app.update.url.manual", "https://stgr-browser.dev/download");

// ---------------------------------------------------------------------------
// VERTICAL TABS
// ---------------------------------------------------------------------------
pref("stgr.verticalTabs.enabled", false);
pref("stgr.verticalTabs.width", 260);
pref("stgr.verticalTabs.animations", true);
pref("stgr.verticalTabs.showPreview", true);
pref("stgr.verticalTabs.showPinnedSection", true);
pref("stgr.verticalTabs.autoHide", false);
pref("stgr.verticalTabs.searchEnabled", true);
pref("stgr.verticalTabs.searchFuzzy", true);
pref("stgr.verticalTabs.searchUrls", true);
pref("stgr.verticalTabs.previewWidth", 280);
pref("stgr.verticalTabs.previewHeight", 175);
pref("stgr.verticalTabs.previewQuality", 70);

// ---------------------------------------------------------------------------
// TAB GROUPS
// ---------------------------------------------------------------------------
pref("stgr.tabGroups.enabled", true);
pref("stgr.tabGroups.showColorDot", true);
pref("stgr.tabGroups.collapseOnStartup", false);
pref("stgr.tabGroups.data", "");

// ---------------------------------------------------------------------------
// MISC
// ---------------------------------------------------------------------------
pref("browser.aboutConfig.showWarning", false);
pref("browser.tabs.allow_transparent_browser", false);
pref("browser.tabs.remote.autostart", true);
pref("browser.tabs.remote.autostart.2", true);
pref("browser.tabs.remote.separatePrivilegedContentProcess", true);
pref("browser.tabs.remote.separatePrivilegedMozillaWebContentProcess", false);
pref("browser.tabs.remote.separateFileUriProcess", true);
pref("browser.tabs.remote.allowLinkedWebInFileUriProcess", false);
pref("browser.link.open_newwindow", 3);
pref("browser.link.open_newwindow.restriction", 0);
pref("browser.ctrlTab.recentlyUsedOrder", false);
pref("browser.backspace_action", 0);
pref("middlemouse.paste", false);
pref("mousewheel.withcontrolkey.action", 3);
pref("general.smoothScroll", true);
pref("general.smoothScroll.msdPhysics.enabled", true);
pref("general.smoothScroll.currentVelocityWeighting", 0.15);
pref("general.smoothScroll.stopDecelerationWeighting", 0.4);

// Disable all Mozilla services
pref("browser.library.activity-stream.enabled", false);
pref("browser.contentblocking.introCount", 99);
pref("browser.messaging-system.whatsNewPanel.enabled", false);
pref("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons", false);
pref("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.features", false);
pref("browser.newtabpage.activity-stream.feeds.discoverystreamfeed", false);
pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);
pref("browser.newtabpage.activity-stream.feeds.topsites", false);
pref("browser.newtabpage.activity-stream.improvesearch.topSiteSearchShortcuts", false);
pref("browser.newtabpage.activity-stream.improvesearch.topSiteSearchShortcuts.havePinned", "");
pref("browser.newtabpage.activity-stream.prerender", false);
pref("browser.newtabpage.activity-stream.showSearch", true);
pref("browser.newtabpage.activity-stream.telemetry", false);
pref("browser.newtabpage.activity-stream.telemetry.structuredIngestion.endpoint", "");
pref("browser.newtabpage.blocked", "");
pref("browser.newtabpage.enabled", true);
pref("browser.partner.link.attribution", "");
pref("browser.privatebrowsing.autostart", false);
pref("browser.privatebrowsing.forceMediaMemoryCache", true);
pref("browser.privatebrowsing.vpnpromourl", "");

// Screenshots
pref("extensions.screenshots.disabled", false);
pref("extensions.screenshots.upload-disabled", true);

// ---------------------------------------------------------------------------
// PLATFORM-SPECIFIC OPTIMIZATIONS
// ---------------------------------------------------------------------------
// These prefs are set for all platforms but only apply where relevant.
// Firefox safely ignores platform-inapplicable prefs at runtime.

// Linux/Wayland - optimized window and GPU behavior
pref("widget.wayland.opaque-region.enabled", true);
pref("widget.use-xdg-desktop-portal.file-picker", 1);

// macOS - Metal rendering, Core Animation compositing, hardware decode
pref("gfx.core-animation.enabled", true);
pref("layers.acceleration.force-enabled", true);
pref("media.hardware-video-decoding.vp9.enabled", true);

// Cross-platform: frame rate targeting
pref("layout.frame_rate", 144);
pref("layout.frame_rate.power_saving", 60);

// Non-native theme rendering (faster than native on all platforms)
pref("widget.non-native-theme.enabled", true);
