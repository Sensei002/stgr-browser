# Self-Hosted Runner Setup Guide

**STGR Browser** is built on Mozilla Firefox's Gecko engine, which requires significant compute resources for compilation. GitHub-hosted runners do not have enough RAM, disk space, or runtime to complete a Firefox build. You **must** use self-hosted runners.

## Why Self-Hosted Runners?

| Requirement | GitHub Hosted | Self-Hosted (Recommended) |
|:---|---:|---:|
| **RAM** | 7 GB | 16-32 GB |
| **Disk** | ~14 GB usable | 80+ GB SSD |
| **Build Time** | Exceeds 6h limit | 1-4 hours |
| **Toolchain** | Limited | Full control |
| **Cost** | Pay per minute | One-time hardware |

## System Requirements

### All Platforms

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16 GB | 32 GB |
| Disk (free) | 60 GB | 100+ GB SSD |
| CPU cores | 4 | 8+ |
| Network | Broadband | Broadband |
| Time (first build) | — | 2-4 hours |

### Platform-Specific Tools

| Platform | Required Software |
|----------|-------------------|
| **Windows** | Visual Studio 2022, MozillaBuild, Rust, Python 3.8+ |
| **Linux** | GCC/Clang, GTK3 dev libs, ALSA/PulseAudio dev, Rust, Python 3.8+ |
| **macOS** | Xcode (full), Homebrew, Rust, Python 3.8+ |

---

## Windows x64 Setup

### 1. Install Visual Studio 2022

- Download from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/)
- Installer → **Desktop development with C++** workload
- **Include** in individual components:
  - MSVC v143 - VS 2022 C++ x64/x86 build tools
  - Windows 10/11 SDK (latest)
  - C++ CMake tools for Windows
  - C++ ATL for v143
- **Path must not contain spaces**

### 2. Install MozillaBuild

```powershell
# Download from Mozilla FTP:
# https://ftp.mozilla.org/pub/mozilla/libraries/win32/MozillaBuildSetup-Latest.exe
# Install to C:\mozilla-build (default)
```

### 3. Install Rust

```powershell
# Download from https://rustup.rs
rustup-init.exe
# When prompted, choose default installation

# Add Windows MSVC target
rustup target add x86_64-pc-windows-msvc
```

### 4. Configure Antivirus Exclusions

**Critical** — without exclusions, builds are 2-5x slower and often fail.

```powershell
# Add these directories to Windows Defender exclusions:
# - C:\mozilla-build
# - C:\actions-runner
# - D:\build (or wherever you put source code)
# - %USERPROFILE%\.mozbuild
```

### 5. Install the GitHub Runner

```powershell
# Create runner directory (path must NOT contain spaces)
mkdir C:\actions-runner
cd C:\actions-runner

# Download from your repository:
# GitHub → Settings → Actions → Runners → New self-hosted runner → Windows
# Follow the on-screen instructions to configure

# Install as a Windows service (run as Administrator)
.\svc install
```

### 6. Configure Runner Labels

When configuring the runner, add these labels:

```
self-hosted, windows, x64
```

> These must match the `runs-on` labels in the workflow files exactly.

### 7. Verify Setup

```powershell
# Open MozillaBuild shell
C:\mozilla-build\start-shell.bat

# Inside the shell, test that mach works
cd /c/build/gecko-dev
./mach --version
```

---

## Linux x64 Setup

### 1. Install System Dependencies

```bash
# Ubuntu/Debian (22.04+ or 24.04+ recommended)
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  build-essential curl git \
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
  nodejs npm \
  llvm-dev clang lld \
  p7zip-full unzip

# For VA-API hardware video decode
sudo apt install -y \
  mesa-va-drivers libva-dev libva-drm2 \
  intel-media-driver  # Intel iGPU only
```

```bash
# Fedora 39+
sudo dnf groupinstall -y "Development Tools" "Development Libraries"
sudo dnf install -y \
  gtk3-devel dbus-glib-devel pulseaudio-libs-devel \
  alsa-lib-devel mesa-libGL-devel mesa-libEGL-devel \
  libavcodec-devel libX11-devel libXext-devel libXrender-devel \
  libxcb-devel libdrm-devel \
  python3 python3-devel nodejs \
  clang lld \
  yasm nasm autoconf2.13
```

### 2. Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup update
```

### 3. Create a Build User (Recommended)

```bash
# Create dedicated user for the runner
sudo useradd -m -s /bin/bash github-runner

# Add to sudo group if needed (for dependency installation)
sudo usermod -aG sudo github-runner
```

### 4. Install the GitHub Runner

```bash
# Create runner directory
sudo mkdir -p /opt/actions-runner
sudo chown github-runner:github-runner /opt/actions-runner
cd /opt/actions-runner

# As the github-runner user:
# GitHub → Settings → Actions → Runners → New self-hosted runner → Linux
# Follow the on-screen instructions

# Install as a systemd service
sudo ./svc.sh install github-runner
sudo ./svc.sh start
```

### 5. Configure Runner Labels

```
self-hosted, linux, x64
```

### 6. Optimize for Build Performance

```bash
# Add to /etc/fstab for better I/O (if using SSDs)
# Add 'noatime,nodiratime' to mount options

# Increase max file watchers (builds create many files)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# For AMD CPUs: use -O3 -march=znver4 (or znver3)
# This is already set in mozconfig-linux
```

---

## macOS Setup

### 1. Install Xcode

```bash
# Install from Mac App Store (free) or:
xcode-select --install

# For full build support, install the complete Xcode app:
# https://apps.apple.com/us/app/xcode/id497799835

# Accept license
sudo xcodebuild -license accept
```

### 2. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Install Dependencies

```bash
# Required system packages
brew install \
  git python@3.11 python@3.12 \
  node npm \
  rustup-init \
  yasm nasm \
  autoconf@2.13 \
  llvm

# Set up Rust
rustup-init -y
source "$HOME/.cargo/env"
rustup update
```

### 4. Install the GitHub Runner

```bash
# Create runner directory
sudo mkdir -p /opt/actions-runner
sudo chown $(whoami):staff /opt/actions-runner
cd /opt/actions-runner

# GitHub → Settings → Actions → Runners → New self-hosted runner → macOS
# Follow the on-screen instructions

# Install as a launchd service
./svc.sh install
./svc.sh start
```

### 5. Configure Runner Labels

```
self-hosted, macos, x64
```

> For Apple Silicon Macs, use labels: `self-hosted, macos, arm64`

### 6. Increase File Descriptor Limits

```bash
# Firefox builds open many files simultaneously
# Add to ~/.zshrc or ~/.bash_profile:
ulimit -n 65536

# For system-wide setting:
sudo launchctl limit maxfiles 65536 200000
```

---

## Registering Runners

### Repository-Level Runner

1. Go to **GitHub → Your Repository → Settings → Actions → Runners**
2. Click **New self-hosted runner**
3. Select your OS and architecture
4. Follow the on-screen download and configuration commands
5. Add labels: `self-hosted`, `[platform]`, `x64` (or `arm64`)

### Organization-Level Runner (if using an org)

1. Go to **GitHub → Organization → Settings → Actions → Runners**
2. Click **New runner**
3. Same steps as above
4. **Advantage**: All repos in the organization can use the runner

---

## Security Considerations

> ⚠️ **WARNING**: Self-hosted runners execute arbitrary code from workflows.
> Forked PRs can run malicious code on your machine.

### DOs

- ✅ Use **private repositories** for self-hosted builds
- ✅ Run in an **isolated VM** or dedicated machine
- ✅ Use a **dedicated low-privilege user account**
- ✅ Apply **OS security patches** regularly
- ✅ Use **firewall rules** to restrict outbound access
- ✅ Set **disk quotas** to prevent full-disk attacks

### DON'Ts

- ❌ Do not use with public repositories
- ❌ Do not run as root/Administrator
- ❌ Do not store secrets/credentials on the runner
- ❌ Do not skip antivirus (Windows) or security updates

### Running Safely with Public Repos

If you must build a public repo:

```yaml
# In your workflow, restrict to trusted branches only
jobs:
  build:
    if: github.event.pull_request.head.repo.full_name == github.repository
```

---

## Monitoring & Maintenance

### Check Runner Status

```bash
# Linux/macOS
sudo ./svc.sh status

# Windows (PowerShell as Admin)
Get-Service "actions.runner.*"
```

### View Runner Logs

```bash
# Linux/macOS
sudo journalctl -u actions.runner.* -f

# Windows
Get-Content "C:\actions-runner\_diag\*.log" -Tail 50
```

### Regular Maintenance

| Task | Frequency |
|------|-----------|
| Update runner software | Monthly |
| Clean old build artifacts | Weekly |
| Update Rust toolchain | Monthly |
| Apply OS security patches | Weekly |
| Check disk space | Weekly |
| Rotate runner tokens | Quarterly |

### Cleaning Disk Space

```bash
# Linux/macOS — clean Firefox build objects
cd /path/to/gecko-dev
./mach clobber

# Remove old cargo registries
rm -rf ~/.cargo/registry/cache/

# Remove downloaded toolchains
rm -rf ~/.mozbuild/_Toolloader/
```

---

## Verifying the Setup

After registering your runner, trigger a **validation-only** workflow run:

```yaml
# Create a simple test workflow to verify:
name: Test Runner
on: workflow_dispatch
jobs:
  test:
    runs-on: [self-hosted, linux, x64]  # match your labels
    steps:
      - run: echo "Runner works! CPU: $(nproc), RAM: $(free -h | grep Mem)"
```

Once the test passes, the runner is ready for full STGR Browser builds.

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Runner offline | Service not running | `sudo ./svc.sh start` |
| Build OOM | Not enough RAM | Add swap: `fallocate -l 16G /swapfile` |
| Disk full during build | No cleanup | `./mach clobber`, delete `~/.mozbuild/cache` |
| Patch fails | Wrong Firefox branch | Update `FIREFOX_BASE_BRANCH` in workflow |
| Linker crashes | Not enough memory | Use LLD: add `-fuse-ld=lld` to mozconfig |
| Runner won't start config | Path has spaces | Move to `C:\actions-runner` or `/opt/actions-runner` |
| Build extremely slow | Antivirus scanning | Add exclusions for build directories |
| `mach` not found | Source not set up | Run `./scripts/setup.sh` first |

---

> **Next Steps:** After setting up your runner, trigger a validation workflow, then a full nightly build. Monitor the first build closely — it downloads toolchains and compiles from scratch, taking 2-4 hours.
