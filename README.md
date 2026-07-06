![STGR Browser](branding/logo.svg)

<p align="center">
  <a href="https://www.steigerdojo.mvp.bd"><strong>STEiGER Dojo</strong></a> —
  <em>Empowering the next generation of developers</em>
</p>

# STGR Browser

**A lightweight, privacy-first, gaming-focused browser built on Mozilla Firefox / Gecko.**

STGR Browser is a fork of Mozilla Firefox that has been stripped of telemetry, tracking, sponsored content, and bloat — then rebuilt with aggressive performance optimizations and a clean, minimal UI.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🔒 **Privacy First** | No telemetry, no tracking, no sponsored content. Zero data collection. |
| 🎮 **Gaming Mode** | Automatic performance optimization when games are running |
| ⚡ **Extreme Performance** | Optimized startup, memory, GPU, and rendering |
| 🎨 **Minimal UI** | Clean, modern interface with dark/light themes |
| 🔌 **Full Extension Support** | Works with thousands of Firefox extensions |
| 📦 **Low RAM Usage** | ~90-120 MB idle, ~120-180 MB normal browsing |
| 🖥️ **Hardware Accelerated** | WebRender, Vulkan, DirectX 12, Metal support |
| 🌐 **Full Web Standards** | Complete HTML5, CSS3, JavaScript ES2025+ support |

## 🎯 Performance Targets

| Scenario | Target RAM |
|----------|-----------|
| Idle (no tabs) | 90-120 MB |
| Normal browsing (5-10 tabs) | 120-180 MB |
| YouTube 1080p video | ~200 MB (best-effort) |
| Gaming Mode | ~30% reduction |

> *Note: Actual memory usage depends on website content and extensions. Targets represent best-effort optimizations within Firefox's architecture.*

## 🔧 Quick Start

### Prerequisites

- **Git**
- **Rust toolchain** (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`)
- **Node.js** 18+
- **Python** 3.8+
- **Build tools** (see [Build Guide](docs/BUILD.md) for platform-specific dependencies)

### Setup & Build

```bash
# 1. Clone this repository
git clone https://github.com/Sensei002/stgr-browser.git
cd stgr-browser

# 2. Run setup (clones Firefox source, applies patches, installs dependencies)
./scripts/setup.sh

# 3. Build STGR Browser
./scripts/build.sh build

# 4. Run STGR Browser
./scripts/build.sh run
```

> **Building Firefox takes 1-3 hours on modern hardware.** The initial clone is ~300MB.

> **Note:** Patches 0010-0015 (Vertical Tabs, Tab Groups, Tab Preview, Auto-Hide, Enhanced Search, STGR Preferences Pane) include new component files that are copied into the Firefox tree. After running `setup.sh`, some manual integration steps may be required for the STGR Preferences pane — see [docs/STGR_PREFERENCES.md](docs/STGR_PREFERENCES.md) for details.

### Platform-Specific Builds

- **Windows**: Use the MozillaBuild shell, run `./scripts/build-windows.sh build`
- **Linux**: Run `./scripts/build-linux.sh deps` first, then `./scripts/build-linux.sh build`
- **macOS**: Run `./scripts/build-macos.sh deps` first, then `./scripts/build-macos.sh build`

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/ARCHITECTURE.md) | Browser architecture and component design |
| [Build Guide](docs/BUILD.md) | Detailed build instructions for all platforms |
| [Developer Guide](docs/DEVELOPER.md) | Development workflow and coding standards |
| [Optimization Guide](docs/OPTIMIZATION.md) | Performance optimization details |
| [Privacy Documentation](docs/PRIVACY.md) | Privacy features and data handling |
| [Gaming Mode](docs/GAMING_MODE.md) | Gaming mode design and configuration |
| [Branding Guide](docs/BRANDING.md) | Branding and theming documentation |
| [Contribution Guide](docs/CONTRIBUTING.md) | How to contribute to STGR Browser |

## 🗺️ Project Structure

```
stgr-browser/
├── branding/          # Branding assets, logos, themes
│   ├── logo.svg       # STGR Browser logo
│   ├── icon.svg       # Application icon
│   ├── theme.json     # Browser theme definition
│   └── icons/         # Generated icons (various sizes)
├── config/            # Build configuration
│   ├── mozconfig      # Smart OS-detecting build config
│   ├── stgr-prefs.js  # Default browser preferences
│   └── search-engines.json
├── scripts/           # Build and development scripts
│   ├── setup.sh       # Environment setup
│   ├── build.sh       # Unified build script (auto-detects OS)
│   ├── apply-patches.sh
│   ├── build-linux.sh
│   ├── build-macos.sh
│   ├── build-windows.sh
│   ├── generate-icons.sh
│   ├── generate-splash.sh
│   ├── verify-patches.sh
│   ├── verify-privacy.sh
│   └── lint-patches.sh
├── patches/           # 15 Firefox optimization patches (0001-0015)
├── docs/              # Comprehensive documentation (12 guides)
├── assets/            # Static assets (splash screen, etc.)
├── gecko-dev/         # Firefox source (cloned by setup.sh)
├── .github/           # CI/CD configuration + issue templates
├── CHANGELOG.md       # Release history
└── SECURITY.md        # Security vulnerability reporting
```

## 🔒 Privacy Promise

STGR Browser **never**:
- Collects telemetry or usage data
- Sends browsing history to any server
- Shows sponsored content or recommendations
- Requires an account
- Uses cloud services
- Includes crypto features
- Includes advertisements
- Ships with AI assistants
- Includes shopping assistants

---

## 🥋 About STEiGER Dojo

**STGR Browser** is developed and maintained by **STEiGER Dojo** — a community-driven organization dedicated to empowering the next generation of developers through open-source software, hands-on learning, and privacy-first technology.

| 🌐 | [steigerdojo.mvp.bd](https://www.steigerdojo.mvp.bd) |
|---|---|
| 🐙 | GitHub: [@Sensei002](https://github.com/Sensei002) |
| 📧 | Contact: steigerdojo@email.com |

> *"Empowering the next generation of developers — one open-source project at a time."*

### What is STEiGER Dojo?

STEiGER Dojo is a digital dojo — a space where developers of all skill levels come together to learn, build, and contribute to meaningful open-source projects. The name reflects our philosophy:

- **STE** — Science, Technology, Engineering
- **i** — Innovation
- **GER** — Growth, Excellence, Resilience
- **Dojo** — A place of focused learning and practice

### Our Mission

- **Build privacy-first software** that respects users as people, not products
- **Teach through doing** — real projects, real skills, real impact
- **Foster open-source communities** where everyone is welcome to contribute
- **Create tools for gamers and power users** who demand performance without compromise

---

## 📄 License

STGR Browser is based on Mozilla Firefox, which is licensed under the Mozilla Public License 2.0.

- **Firefox code**: MPL-2.0
- **STGR modifications**: MPL-2.0
- **STGR branding and assets**: All rights reserved (STEiGER Dojo)

See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>STGR Browser</strong> — a project by <a href="https://www.steigerdojo.mvp.bd">STEiGER Dojo</a><br>
  <em>Empowering the next generation of developers</em>
</p>
