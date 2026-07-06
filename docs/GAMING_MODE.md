# STGR Browser Gaming Mode

## Overview

Gaming Mode is a flagship STGR Browser feature that automatically optimizes browser performance when you're gaming. It detects when a game is running and automatically applies performance optimizations to free up system resources.

## How It Works

### Detection

Gaming Mode detects gaming activity through two mechanisms:

1. **Process Detection** (primary, Windows)
   - Monitors running processes for known game executables
   - Default game list includes 50+ popular games
   - Users can add custom game processes

2. **Fullscreen Detection** (fallback, all platforms)
   - Detects when any browser tab enters fullscreen
   - Useful for browser-based games

### Detection Threshold

- **Latency**: 1-5 seconds after game launch
- **Cooldown**: 30 seconds after game closes (prevents toggling)
- **Poll Interval**: Checks every 5 seconds

## Applied Optimizations

When Gaming Mode activates, the following changes are applied:

### Memory Optimizations

| Setting | Normal | Gaming Mode |
|---------|--------|-------------|
| Content processes | 4 | 2 |
| Extension processes | 1 | 0 (disabled) |
| Image cache | 200 KB | 100 KB |
| Media cache | 50 MB | 25 MB |
| JS memory limit | 256 MB | 128 MB |

### Performance Optimizations

| Setting | Normal | Gaming Mode |
|---------|--------|-------------|
| Session save interval | 60s | 120s |
| Network connections | 64 | 32 |
| Speculative parsing | On | Off |
| Image decode immediately | On | Off |
| Background animation FPS | 60 | 10 |
| Timer resolution | Normal | Low |

### Tab Management

- **Background tabs are discarded** (not just suspended)
- **Only the active tab** remains loaded
- **Pinned tabs are preserved** but suspended
- **Tabs restore on click** (lazy loading)

## Configuration

### Enabling/Disabling

**Via Settings UI** (recommended):
`Settings > Performance > Gaming Mode`

**Via about:config**:
- `stgr.gamingMode.enabled` - Enable/disable (boolean)
- `stgr.gamingMode.pollInterval` - Detection interval in ms (default: 5000)

### Adding Custom Game Detection

**Via Settings**:
`Settings > Performance > Gaming Mode > Custom Games`

**Via about:config**:
`stgr.gamingMode.customProcesses` - Comma-separated list of process names

### API

Gaming Mode can be toggled programmatically:

```javascript
// Check status
Services.prefs.getBoolPref("stgr.gamingMode.enabled");

// Toggle
Services.prefs.setBoolPref("stgr.gamingMode.enabled", !currentValue);
```

## Performance Impact

| Metric | Without Gaming Mode | With Gaming Mode | Savings |
|--------|-------------------|------------------|---------|
| RAM usage | 180 MB | 90-120 MB | ~40% |
| CPU usage (idle) | 2-5% | 0.5-1% | ~75% |
| GPU memory | ~100 MB | ~50 MB | ~50% |
| Background tabs | Full resources | Discarded | 100% |
| Network activity | Normal polling | Minimal | Significant |

> *Results vary based on system configuration and active tabs.*

## Known Limitations

1. **Process detection** only works on Windows (uses `nsIProcessEnumerator`)
2. **macOS** and **Linux** rely on fullscreen detection
3. **Some anti-cheat software** may interfere with process enumeration
4. **Extensions** are disabled in Gaming Mode (may cause temporary issues)
5. **Discarded tabs** need to reload when clicked (adds ~1-2 seconds)

## Future Enhancements

Planned improvements (contributions welcome):

- [ ] macOS/Linux process detection via OS-native APIs
- [ ] User-configurable optimization profiles
- [ ] Per-game optimization settings
- [ ] Game library integration (Steam, Epic)
- [ ] Resource monitoring dashboard
- [ ] Automatic profile switching per game
- [ ] Benchmark mode to measure gains
- [ ] Integration with Windows Game Mode API

## Development

### Component Structure

```
browser/components/gaming/
├── GamingMode.jsm          # Main Gaming Mode service
├── GamingModeUI.jsm        # Gaming Mode UI elements
├── content/
│   └── gaming-indicator.js # Status indicator
├── locales/
│   └── en-US/
│       └── gaming.ftl      # Localization strings
└── test/
    └── test_gaming_mode.js # Unit tests
```

### Adding Game Detection

```javascript
// In GamingMode.jsm
const MY_GAMES = ["my-game.exe", "launcher.exe"];

// Or via preferences
Services.prefs.setCharPref(
  "stgr.gamingMode.customProcesses",
  "my-game.exe,launcher.exe"
);
```

---

*Gaming Mode is designed to be invisible - it should just make your games run better without you having to think about it.*
