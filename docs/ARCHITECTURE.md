# STGR Browser Architecture

## Overview

STGR Browser is built on Mozilla's Gecko rendering engine (Firefox). The architecture follows Firefox's multi-process model with STGR-specific modifications for performance, privacy, and gaming features.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STGR Browser (UI)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Toolbar  │ │  Tabs    │ │  Sidebar │ │  Gaming Mode  │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│              Gecko Rendering Engine (Firefox)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │  HTML    │ │  CSS     │ │ JavaScript│ │  WebRender    │  │
│  │  Parser  │ │  Engine  │ │  Engine  │ │  (GPU Render) │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Multi-Process Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │  Parent  │ │  Content │ │  GPU     │ │  Extension    │  │
│  │ Process  │ │ Process  │ │ Process  │ │  Process      │  │
│  │  x1     │ │  x4     │ │  x1     │ │  x1          │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Platform Layer                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Windows  │ │  Linux   │ │  macOS   │ │  Security    │  │
│  │ D3D/VK   │ │  Vulkan  │ │  Metal   │ │  Sandbox     │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Process Model

STGR Browser uses Firefox's Electrolysis (e10s) multi-process architecture with STGR-specific tuning:

| Process Type | Count | Purpose |
|-------------|-------|---------|
| **Parent** | 1 | UI, browser chrome, all services |
| **Content** | 4 (default) | Web page rendering | 
| **GPU** | 1 | WebRender compositing |
| **Extensions** | 1 | Extension processing (when needed) |
| **File** | 1 | Local file access |
| **Socket** | 1 | Network processing (when needed) |

In **Gaming Mode**, content processes reduce to 2.

## Memory Management

STGR implements aggressive memory optimization:

1. **Tab Discarding**: Background tabs inactive for 5+ minutes are automatically discarded
2. **Cache Trimming**: Reduced image, font, and media cache sizes
3. **GC Optimization**: More aggressive JavaScript garbage collection
4. **Memory Pressure Handling**: Immediate tab discarding on low memory
5. **Process Limits**: Reduced concurrent content processes
6. **Delayed Initialization**: Non-critical services start after first paint

## GPU Pipeline

```
Web Content → WebRender Display List → GPU Compositing → Screen
                   ↓                       ↓
              Picture Tiles           Hardware Decode
              (512x512)               (D3D11/VA-API/VTB)
```

STGR enables:
- **WebRender**: Always-on GPU-accelerated rendering
- **GPU Rasterization**: Canvas and CSS rendering on GPU
- **Hardware Video Decoding**: D3D11 (Windows), VA-API (Linux), VTB (macOS)
- **DirectComposition**: Windows 10+ composition
- **Vulkan**: Where available

## Gaming Mode Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Gaming Mode Service                  │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Process  │→│ Preference│→│ Resource         │  │
│  │ Detector │  │ Manager  │  │ Optimizer       │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│       ↓             ↓                ↓              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Game     │  │ Apply    │  │ Tab Suspender    │  │
│  │ Detected │  │ Prefs    │  │ Background       │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## Privacy Architecture

All data collection is removed at multiple levels:

1. **Build Level**: Telemetry components excluded from compilation
2. **Source Level**: Telemetry code stubbed out
3. **Preference Level**: All telemetry prefs disabled by default
4. **Runtime Level**: No background network requests
5. **UI Level**: No privacy-intrusive features exposed

## Key Dependencies

| Component | Technology | Notes |
|-----------|-----------|-------|
| Rendering Engine | Gecko (Firefox) | Full web standards support |
| JavaScript | SpiderMonkey | Firefox's JS engine |
| GPU Rendering | WebRender | Mozilla's GPU renderer |
| Network | Necko | Firefox's networking library |
| Security | NSS | Network Security Services |
| Media | FFmpeg | Hardware-accelerated decoding |
| Extensions | WebExtensions | Full Firefox API compatibility |

## STGR Components

| Component | Location | Description |
|-----------|----------|-------------|
| Gaming Mode | `gecko-dev/browser/components/gaming/` | Gaming detection and optimization |
| STGR Theme | `branding/theme.json` | Default browser theme |
| STGR Prefs | `config/stgr-prefs.js` | Configuration defaults |
| STGR Branding | `branding/` | Branding assets |
