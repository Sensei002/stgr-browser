# STGR Browser Build Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Platform-Specific Setup](#platform-specific-setup)
3. [Building STGR Browser](#building-stgr-browser)
4. [Build Configuration](#build-configuration)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required for all platforms

| Tool | Minimum Version | Installation |
|------|----------------|--------------|
| Git | 2.30+ | [git-scm.com](https://git-scm.com) |
| Rust | 1.70+ | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Python | 3.8+ | [python.org](https://python.org) |
| clang/LLVM | 16+ | Platform-specific |

### Storage Requirements

| Item | Size |
|------|------|
| Firefox source (clone) | ~300 MB |
| Build objects | ~20-40 GB |
| STGR project | ~1 MB |
| **Total** | **~20-40 GB** |

### Time Requirements

| Build Type | Time |
|-----------|------|
| First build (full) | 1-3 hours |
| Incremental build | 5-30 minutes |
| Source clone | 5-30 minutes |
| Bootstrap deps | 10-30 minutes |

## Platform-Specific Setup

### Windows

#### Prerequisites

1. **Visual Studio 2022** (Community is free)
   - Workload: "Desktop development with C++"
   - Include: MSVC v143, Windows 10/11 SDK, C++ CMake tools

2. **MozillaBuild**
   - Download: [MozillaBuild](https://firefox-source-docs.mozilla.org/setup/windows_build.html)
   - Extract to: `C:\mozilla-build`
   - Uses MSYS2 environment with Mozilla's build tools

3. **Rust with Windows target**
   ```bash
   rustup target add x86_64-pc-windows-msvc
   ```

4. **DirectX SDK** - Included with Windows 10/11 SDK

#### Build Steps

```bash
# Open MozillaBuild shell
C:\mozilla-build\start-shell.bat

# Navigate to project
cd /c/Users/YourName/stgr-browser

# Run setup (clones Firefox + applies patches)
./scripts/setup.sh

# Build
./scripts/build-windows.sh build

# The installer will be in gecko-dev/obj-build-stgr/dist/
```

### Linux

#### Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential curl git \
  libgtk-3-dev libdbus-glib-1-dev \
  libpulse-dev libasound2-dev \
  libavcodec-dev libavformat-dev libswscale-dev \
  libx11-dev libxext-dev libxrender-dev \
  mesa-common-dev libegl1-mesa-dev libgles2-mesa-dev \
  libpango1.0-dev libcairo2-dev libatk1.0-dev \
  libgdk-pixbuf2.0-dev libxdamage-dev libxcomposite-dev \
  libxfixes-dev libnotify-dev \
  yasm nasm autoconf2.13 \
  python3 python3-dev python3-pip \
  nodejs npm llvm-dev clang lld

# Fedora
sudo dnf groupinstall "Development Tools" "Development Libraries"
sudo dnf install gtk3-devel dbus-glib-devel pulseaudio-libs-devel \
  alsa-lib-devel mesa-libGL-devel libavcodec-devel \
  libX11-devel libXext-devel libXrender-devel \
  python3 python3-devel nodejs clang lld
```

#### Build Steps

```bash
# Install dependencies
./scripts/build-linux.sh deps

# Run setup
./scripts/setup.sh

# Build
./scripts/build-linux.sh build
```

### macOS

#### Prerequisites

```bash
# Install Xcode from Mac App Store
# Install Command Line Tools
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
./scripts/build-macos.sh deps
```

#### Build Steps

```bash
# Run setup
./scripts/setup.sh

# Build (native)
./scripts/build-macos.sh build

# Build (universal binary for Intel + Apple Silicon)
./scripts/build-macos.sh build-universal
```

## Building STGR Browser

### Quick Build

```bash
# Setup (first time only)
./scripts/setup.sh

# Build release
./scripts/build.sh build

# Build and run
./scripts/build.sh run

# Create installer
./scripts/build.sh package
```

### Build Variants

| Command | Description |
|---------|-------------|
| `./scripts/build.sh build` | Release build (optimized) |
| `./scripts/build.sh build-debug` | Debug build (with symbols) |
| `./scripts/build.sh build-clean` | Clean build (removes objects first) |
| `./scripts/build.sh package` | Create installer package |
| `./scripts/build.sh test` | Run test suite |
| `./scripts/build.sh lint` | Run linters |

### Direct Mach Commands

For advanced usage, you can use Mozilla's mach directly:

```bash
cd gecko-dev

# Configure build
./mach configure

# Build
./mach build

# Build and run
./mach run

# Run specific tests
./mach test browser/components/gaming

# Create language pack
./mach build langpack

# Package for distribution
./mach build package
```

## Build Configuration

### STGR mozconfig

The build is configured via `config/mozconfig`. Key settings:

```bash
# Architecture
ac_add_options --enable-optimize="-O2 -march=native"
ac_add_options --enable-lto
ac_add_options --enable-pgo

# STGR Branding
ac_add_options --with-app-name=stgr-browser
ac_add_options --with-app-basename=STGR
ac_add_options --with-branding=stgr/branding

# Graphics
ac_add_options --enable-webrender

# Remove Mozilla services
ac_add_options --disable-crashreporter
ac_add_options --disable-tests
```

### Preference Overrides

`config/stgr-prefs.js` contains all STGR Browser default preferences. These are loaded at runtime.

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `./mach build` fails with linker error | Increase swap space (need 8GB+ RAM) |
| Patch application fails | Check for `.rej` files, manually resolve conflicts |
| Rust not found | Run `rustup update` and ensure `~/.cargo/bin` is in PATH |
| Python version mismatch | Ensure Python 3.8+ is default (`python3 --version`) |
| Out of disk space | Clean with `./mach clobber` |
| Missing build dependencies | Run platform-specific `deps` command |

### Getting Help

- **Documentation**: [docs/](/docs) directory
- **Firefox Build Docs**: [firefox-source-docs.mozilla.org](https://firefox-source-docs.mozilla.org/setup/)
