// ============================================================================
// STGR Browser - Default Browser Configuration
// ============================================================================
// This file should be placed in the STGR Browser application directory
// and loaded at startup to apply browser-level defaults.
// ============================================================================

const STGR_DEFAULTS = {
  // Browser identity
  app: {
    name: "STGR Browser",
    vendor: "STGR",
    version: "1.0.0",
    buildID: "20260701",
    appID: "{stgr-browser-id}",
    platformVersion: "130.0",
  },

  // Homepage configuration
  homepage: {
    url: "about:home",
    newTab: "about:newtab",
    // Custom STGR about:home will be created in the UI layer
  },

  // Default profile settings
  profile: {
    name: "default",
    isDefault: true,
    createOnStartup: true,
  },

  // Proxy configuration
  proxy: {
    type: "system",
    http: "",
    ssl: "",
    ftp: "",
    socks: "",
    socksVersion: 5,
    socksRemoteDNS: false,
    autoLogin: false,
    useProxyForDNS: false,
  },

  // Certificate settings
  certificates: {
    trustAnchors: "builtin",
    ocspEnabled: true,
    ocspRequire: true,
    hpkpEnabled: true,
  },

  // Content blocking levels
  contentBlocking: {
    strict: {
      trackingProtection: true,
      fingerprinting: true,
      cryptomining: true,
      socialTracking: true,
      emailTracking: true,
      thirdPartyCookies: "block-all",
    },
    standard: {
      trackingProtection: true,
      fingerprinting: false,
      cryptomining: false,
      socialTracking: true,
      emailTracking: true,
      thirdPartyCookies: "block-cross-site",
    },
    custom: {
      trackingProtection: true,
      fingerprinting: false,
      cryptomining: false,
      socialTracking: false,
      emailTracking: false,
      thirdPartyCookies: "allow",
    },
  },

  // Gaming mode whitelist (process names to detect)
  gamingDetection: {
    whitelist: [
      "game.exe", "eldenring.exe", "steam.exe", "battle.net.exe",
      "epicgameslauncher.exe", "valorant.exe", "csgo.exe", "cs2.exe",
      "dota2.exe", "leagueclient.exe", "lol.exe", "fortnite.exe",
      "minecraft.exe", "rocketleague.exe", "apexlegends.exe",
      "overwatch.exe", "destiny2.exe", "cod.exe", "modernwarfare.exe",
      "gta5.exe", "gta5_enhanced.exe", "r6.exe", "rainbow6.exe",
      "ffxiv.exe", "wow.exe", "gw2.exe", "eac.exe", "battleye.exe",
      "r5apex.exe", "tlclient.exe", "ubisoftconnect.exe",
      "galaxyclient.exe", "xboxapp.exe", "xbox.exe",
    ],
    // How often to check for gaming processes (ms)
    pollInterval: 5000,
    // How long after game closes to disable gaming mode (ms)
    cooldownPeriod: 30000,
  },

  // Auto-update configuration
  update: {
    server: "https://updates.stgr-browser.dev",
    channel: "release",
    interval: 86400000, // 24 hours
    backgroundDownload: true,
    stagingEnabled: true,
    enableRollback: true,
  },

  // Performance benchmarking thresholds
  performance: {
    // Maximum number of concurrent content processes
    maxContentProcesses: 4,
    // Memory pressure threshold (MB)
    memoryPressureThreshold: 256,
    // Tab discard timeout (ms) - tabs inactive for this long may be discarded
    tabDiscardTimeout: 300000, // 5 minutes
    // Maximum session history entries per tab
    maxSessionHistory: 50,
    // Cache sizes (KB)
    imageCacheMaxSize: 204800,
    mediaCacheSize: 51200,
    // JavaScript memory limit (MB)
    jsMemoryMax: 256,
  },

  // Feature flags
  features: {
    gamingMode: true,
    verticalTabs: true,
    tabGroups: true,
    pictureInPicture: true,
    readerMode: true,
    pdfViewer: true,
    qrGenerator: true,
    screenshotTool: true,
    darkMode: true,
    autoTheme: true,
    hardwareAcceleration: true,
    webrender: true,
    vulkanSupport: true,
    dxSupport: true,
    openGLFallback: true,
  },
};

// Export for use in build system
if (typeof module !== "undefined") {
  module.exports = STGR_DEFAULTS;
}
