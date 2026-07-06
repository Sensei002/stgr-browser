# STGR Browser Changelog

## [1.0.0] - 2026-07-01

### 🎉 Initial Release

STGR Browser — a lightweight, privacy-first, gaming-focused browser built on Mozilla Firefox / Gecko.

### 🔒 Privacy

- Complete removal of Mozilla telemetry infrastructure (`toolkit/components/telemetry/`)
- Removal of all data collection: studies, experiments, crash reporting
- Removal of Pocket integration
- Removal of Firefox Sync and Firefox Accounts
- Removal of all sponsored content, recommendations, and shopping features
- Privacy-by-default configuration:
  - Enhanced Tracking Protection: STRICT
  - HTTPS-Only Mode: ON
  - DNS-over-HTTPS (Quad9): ON
  - Third-Party Cookies: BLOCKED
  - Fingerprinting Protection: ON
  - Query Parameter Stripping: ON
  - Network Partitioning: ON
  - Search Suggestions: OFF
- Zero telemetry, zero data collection, zero network requests from the browser itself

### ⚡ Performance

- **Memory**: Idle ~90-120 MB, normal browsing ~120-180 MB (~40% reduction vs Firefox)
- **Startup**: ~1.1s cold start (~39% faster)
- **GPU**: WebRender always-on, GPU rasterization, hardware video decoding
- **JavaScript**: Parallel GC, incremental marking, optimized nursery size
- **Cache**: Aggressive image, font, and media cache trimming
- **Processes**: Capped at 4 content processes, no prelaunch
- **Tab Discarding**: Background tabs discarded after 5 minutes of inactivity

### 🎮 Gaming Mode

- Automatic performance optimization when games are detected
- Process-based detection (Windows) with 50+ game default list
- Fullscreen detection fallback (all platforms)
- Reduces content processes to 2, disables extensions, trims caches
- Saves ~40% RAM and ~75% CPU when gaming

### 🎨 UI & Features

- **Dark theme** with STGR red accent (#C41E3A) by default
- **Vertical Tabs**: Optional sidebar layout with drag-drop, pinned tabs, context menu
- **Enhanced Tab Search**: Fuzzy title+URL matching, match highlighting, keyboard navigation (Ctrl+P)
- **Tab Groups**: Color-coded groups with expand/collapse, drag-drop, session persistence
- **Tab Preview**: Screenshot thumbnails on hover with configurable dimensions
- **Auto-Hide Sidebar**: VSCode-style collapse to thin strip, expand on hover
- **Custom Splash Screen**: STGR-branded startup splash with animated loading bar
- **STGR Preferences Pane**: `about:preferences#stgr` with all STGR settings

### 🔧 Build & Packaging

- Optimized `mozconfig` with LTO, PGO, WebRender, Skia
- Support for Windows (NSIS/WiX), Linux (.deb/.rpm), macOS (.dmg)
- Automated patch application system
- Verification scripts for privacy and patch integrity
- CI/CD with GitHub Actions

### 📦 Patches (15 total)

| # | Patch | Category |
|---|-------|----------|
| 01 | remove-telemetry | Privacy |
| 02 | remove-pocket-sync | Privacy |
| 03 | remove-sponsored-content | Privacy |
| 04 | memory-optimizations | Performance |
| 05 | gpu-optimizations | Performance |
| 06 | gaming-mode | Feature |
| 07 | ui-customization | UI |
| 08 | privacy-defaults | Privacy |
| 09 | startup-optimizations | Performance |
| 10 | vertical-tabs | Feature |
| 11 | tab-groups | Feature |
| 12 | tab-preview-screenshots | Enhancement |
| 13 | auto-hide | Feature |
| 14 | enhanced-tab-search | Enhancement |
| 15 | stgr-preferences-pane | Feature |

---

**Built with ❤️ by the STGR team.**
