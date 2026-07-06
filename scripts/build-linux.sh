#!/bin/bash
# ============================================================================
# STGR Browser - Linux Build Script
# ============================================================================
# Builds STGR Browser for Linux.
#
# Prerequisites (Ubuntu/Debian):
#   sudo apt install build-essential curl git gcc-multilib g++-multilib \
#     libc6-dev libstdc++-12-dev libgtk-3-dev libdbus-glib-1-dev \
#     libgconf2-dev libpulse-dev libasound2-dev librsvg2-dev libxml2-dev \
#     libxslt1-dev libsqlite3-dev libavcodec-dev libavformat-dev \
#     libswscale-dev libx11-dev libxext-dev libxrender-dev libxcb-shm0-dev \
#     libxcb-icccm4-dev libxcb-image0-dev libxcb-keysyms1-dev \
#     libxcb-randr0-dev libxcb-render-util0-dev libxcb-shape0-dev \
#     libxcb-sync1-dev libxcb-util-dev libxcb-xfixes0-dev \
#     libxcb-xkb-dev libxcb-xv0-dev libxcb-xtest0-dev libxcb1-dev \
#     mesa-common-dev libegl1-mesa-dev libgles2-mesa-dev libgl1-mesa-dev \
#     libglu1-mesa-dev libxft-dev libxinerama-dev libxkbfile-dev \
#     libxmu-dev libxpm-dev libxt-dev libxkbcommon-x11-dev \
#     libpci-dev libglib2.0-dev libpango1.0-dev libatk1.0-dev \
#     libcairo2-dev libgdk-pixbuf2.0-dev libxdamage-dev \
#     libxcomposite-dev libxfixes-dev libnotify-dev libevent-dev \
#     yasm nasm autoconf2.13 python3 python3-dev python3-pip \
#     nodejs npm llvm-dev clang lld
#
# Prerequisites (Fedora):
#   sudo dnf groupinstall "Development Tools" "Development Libraries"
#   sudo dnf install gcc-c++ gtk3-devel dbus-glib-devel pulseaudio-libs-devel \
#     alsa-lib-devel librsvg2-devel libxml2-devel libxslt-devel sqlite-devel \
#     libavcodec-devel libavformat-devel libswscale-devel libX11-devel \
#     libXext-devel libXrender-devel libxcb-devel mesa-libGL-devel \
#     mesa-libEGL-devel mesa-libgles2-devel libXt-devel libXmu-devel \
#     libXpm-devel libXft-devel libXinerama-devel libXcomposite-devel \
#     libXdamage-devel libXfixes-devel pango-devel cairo-devel \
#     atk-devel gdk-pixbuf2-devel notofonts-devel yasm nasm \
#     python3 python3-devel python3-pip nodejs npm clang lld
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STGR_SOURCE_DIR="${STGR_SOURCE_DIR:-$PROJECT_ROOT/gecko-dev}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_pass()  { echo -e "${GREEN}[PASS]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/fedora-release ]; then
        echo "fedora"
    else
        echo "unknown"
    fi
}

# ============================================================================
# VA-API / Hardware Video Acceleration Detection
# ============================================================================
# STGR Browser uses VA-API on Linux for hardware-accelerated video decoding.
# This requires the correct GPU driver to be installed.
#
# Required packages by GPU vendor:
#
#   Intel (Gen8+ / Broadwell+):
#     Ubuntu:  sudo apt install intel-media-driver
#     Fedora:  sudo dnf install intel-media-driver
#     Arch:    sudo pacman -S intel-media-driver
#
#   AMD (GCN+ / all modern):
#     Ubuntu:  sudo apt install mesa-va-drivers
#     Fedora:  sudo dnf install mesa-va-drivers
#     Arch:    sudo pacman -S mesa-va-drivers
#
#   NVIDIA (proprietary driver 545.23.06+):
#     Ubuntu:  sudo apt install nvidia-driver-545 libva-nvidia-driver
#     Fedora:  sudo dnf install akmod-nvidia libva-nvidia-driver
#     Arch:    sudo pacman -S nvidia nvidia-utils libva-nvidia-driver
#
# Multi-GPU detection:
#   If you have an iGPU + dGPU, set MOZ_DRM_DEVICE to the iGPU's render node.
#   Example: export MOZ_DRM_DEVICE=/dev/dri/renderD128
# ============================================================================

# Detect the GPU vendor for VA-API driver recommendations
detect_gpu_vendor() {
    # Try lspci first (fastest)
    if command -v lspci &>/dev/null; then
        if lspci -nn 2>/dev/null | grep -qi "vga.*\|3d.*\|display.*" | grep -qi "intel"; then
            echo "intel"
            return
        fi
        if lspci -nn 2>/dev/null | grep -qi "vga.*\|3d.*\|display.*" | grep -qi "amd\|ati"; then
            echo "amd"
            return
        fi
        if lspci -nn 2>/dev/null | grep -qi "vga.*\|3d.*\|display.*" | grep -qi "nvidia"; then
            echo "nvidia"
            return
        fi
    fi

    # Fallback: check /sys/class/drm render nodes for driver name
    for render in /sys/class/drm/render*; do
        if [ -f "$render/device/driver" ]; then
            local driver
            driver=$(readlink "$render/device/driver" 2>/dev/null | xargs basename 2>/dev/null || true)
            case "$driver" in
                i915)   echo "intel"; return ;;
                amdgpu) echo "amd";   return ;;
                nouveau) echo "nvidia"; return ;;
                nvidia) echo "nvidia"; return ;;
            esac
        fi
    done

    echo "unknown"
}

# Suggest the correct VA-API driver package for the detected distro + GPU
suggest_vaapi_driver() {
    local gpu_vendor="$1"
    local distro="$2"

    case "$gpu_vendor" in
        intel)
            case "$distro" in
                ubuntu|debian)    echo "intel-media-driver" ;;
                fedora)           echo "intel-media-driver" ;;
                arch|manjaro)     echo "intel-media-driver" ;;
                *)                echo "intel-media-driver (or vaapi-intel-driver on older systems)" ;;
            esac
            ;;
        amd)
            case "$distro" in
                ubuntu|debian)    echo "mesa-va-drivers" ;;
                fedora)           echo "mesa-va-drivers" ;;
                arch|manjaro)     echo "mesa-va-drivers" ;;
                *)                echo "mesa-va-drivers" ;;
            esac
            ;;
        nvidia)
            case "$distro" in
                ubuntu|debian)    echo "libva-nvidia-driver (requires nvidia-driver-545+)" ;;
                fedora)           echo "libva-nvidia-driver (requires akmod-nvidia)" ;;
                arch|manjaro)     echo "libva-nvidia-driver (requires nvidia-utils)" ;;
                *)                echo "libva-nvidia-driver + proprietary NVIDIA driver" ;;
            esac
            ;;
        *)
            echo "<unknown GPU — check https://wiki.archlinux.org/title/Hardware_video_acceleration>"
            ;;
    esac
}

# Check if VA-API is available and working
check_vaapi() {
    echo ""
    echo "--- VA-API / Hardware Video Decode Check ---"

    local gpu_vendor
    gpu_vendor=$(detect_gpu_vendor)
    log_info "Detected GPU vendor: $gpu_vendor"

    local distro
    distro=$(detect_distro)

    # Suggest the correct driver
    local driver
    driver=$(suggest_vaapi_driver "$gpu_vendor" "$distro")
    log_info "Recommended VA-API driver: $driver"

    # Check if a VA-API driver is already loaded by looking at /dev/dri
    local render_nodes=""
    if [ -d /dev/dri ]; then
        render_nodes=$(ls /dev/dri/render* 2>/dev/null || true)
    fi

    if [ -n "$render_nodes" ]; then
        log_pass "DRM render nodes found:"
        for node in $render_nodes; do
            echo "         $node"
        done

        # Try vainfo if available to check VA-API actually works
        if command -v vainfo &>/dev/null; then
            local vainfo_out
            vainfo_out=$(vainfo 2>&1 | head -10) || true
            if echo "$vainfo_out" | grep -qi "libva error\|failed\|not found"; then
                log_warn "VA-API installed but not working properly:"
                echo "         $vainfo_out" | while IFS= read -r line; do
                    echo "         $line"
                done
                log_info "Install the recommended driver: $driver"
            else
                log_pass "VA-API appears to be working"
            fi
        else
            log_warn "'vainfo' not found — install it to verify VA-API:"
            case "$distro" in
                ubuntu|debian)  echo "         sudo apt install vainfo" ;;
                fedora)         echo "         sudo dnf install vainfo" ;;
                arch|manjaro)   echo "         sudo pacman -S libva-utils" ;;
                *)              echo "         Install 'libva-utils' package for your distribution" ;;
            esac
            log_info "Driver to install: $driver"
        fi
    else
        log_warn "No DRM render nodes found at /dev/dri/render*"
        log_info "Install the VA-API driver: $driver"
        log_info "After installing, reboot or reload the driver."
    fi

    # Recommend MOZ_DRM_DEVICE for multi-GPU setups
    local render_count
    render_count=$(echo "$render_nodes" | wc -l | tr -d ' ')
    if [ "$render_count" -gt 1 ]; then
        echo ""
        log_info "Multiple DRM devices detected (multi-GPU system)."
        echo "         To ensure correct GPU is used, set MOZ_DRM_DEVICE:"
        echo ""
        for node in $render_nodes; do
            local node_num
            node_num=$(echo "$node" | grep -oP 'renderD\K\d+' || true)
            echo "           export MOZ_DRM_DEVICE=$node"
        done
        echo ""
        echo "         Typically renderD128 = iGPU (Intel/AMD integrated)"
        echo "         and renderD129 = dGPU (discrete/NVIDIA)."
        echo "         Use the iGPU for video decode to save power."
    fi

    # Check if MOZ_DRM_DEVICE is already set
    if [ -n "${MOZ_DRM_DEVICE:-}" ]; then
        log_info "MOZ_DRM_DEVICE is already set to: $MOZ_DRM_DEVICE"
        if [ ! -e "$MOZ_DRM_DEVICE" ]; then
            log_warn "But the device does not exist! Check /dev/dri/ for available nodes."
        fi
    fi

    echo ""
}

# Install the recommended VA-API driver for this system (if --install-vaapi flag given)
install_vaapi_driver() {
    local gpu_vendor
    gpu_vendor=$(detect_gpu_vendor)
    local distro
    distro=$(detect_distro)
    local driver
    driver=$(suggest_vaapi_driver "$gpu_vendor" "$distro")

    # Extract just the package name (strip explanations after parenthetical)
    local pkg
    pkg=$(echo "$driver" | sed 's/ (.*)//')

    if [ "$pkg" = "unknown" ] || [ "$gpu_vendor" = "unknown" ]; then
        log_warn "Could not determine GPU vendor or package name."
        log_info "Please install the VA-API driver manually."
        return
    fi

    log_info "Installing VA-API driver: $pkg..."

    case "$distro" in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y "$pkg" vainfo 2>/dev/null || \
            sudo apt install -y "$pkg"
            ;;
        fedora)
            sudo dnf install -y "$pkg" libva-utils 2>/dev/null || \
            sudo dnf install -y "$pkg"
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm "$pkg" libva-utils 2>/dev/null || \
            sudo pacman -S --noconfirm "$pkg"
            ;;
        *)
            log_warn "Unknown distro — please install '$pkg' manually."
            ;;
    esac

    log_success "VA-API driver installed! Reboot or reload graphics stack."
}

# Install Linux dependencies
install_deps() {
    log_info "Installing build dependencies for Linux..."
    
    local distro=$(detect_distro)
    log_info "Detected distribution: $distro"
    
    case "$distro" in
        ubuntu|debian)
            log_info "Installing Debian/Ubuntu dependencies..."
            sudo apt update
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
                nodejs npm llvm-dev clang lld \
                libxcb-shm0-dev libxcb-icccm4-dev libxcb-image0-dev \
                libxcb-keysyms1-dev libxcb-randr0-dev libxcb-render-util0-dev \
                libxcb-shape0-dev libxcb-sync1-dev libxcb-util-dev \
                libxcb-xfixes0-dev libxcb-xkb-dev libxcb1-dev
            ;;
        fedora)
            log_info "Installing Fedora dependencies..."
            sudo dnf groupinstall -y "Development Tools" "Development Libraries"
            sudo dnf install -y \
                gtk3-devel dbus-glib-devel pulseaudio-libs-devel \
                alsa-lib-devel \
                libavcodec-devel libavformat-devel libswscale-devel \
                libX11-devel libXext-devel libXrender-devel \
                mesa-libGL-devel mesa-libEGL-devel mesa-libgles2-devel \
                pango-devel cairo-devel atk-devel gdk-pixbuf2-devel \
                libXdamage-devel libXcomposite-devel libXfixes-devel \
                libnotify-devel yasm nasm \
                python3 python3-devel python3-pip nodejs npm clang lld
            ;;
        *)
            log_warn "Unknown distribution. Please install build dependencies manually."
            log_warn "See: https://firefox-source-docs.mozilla.org/setup/linux_build.html"
            ;;
    esac
    
    log_success "Dependencies installed!"
    check_vaapi
}

build_linux_release() {
    log_info "Building STGR Browser for Linux (release)..."
    check_vaapi

    cd "$STGR_SOURCE_DIR"

    export MOZ_BUILD_DATE=20260701
    export MOZ_AUTOMATION=1
    export MOZCONFIG="$PROJECT_ROOT/config/mozconfig"

    ./mach build
    ./mach build package

    cd "$PROJECT_ROOT"
    log_success "Linux build complete!"
    
    local output_dir="$STGR_SOURCE_DIR/obj-build-stgr/dist"
    if [ -d "$output_dir" ]; then
        log_info "Package available at:"
        ls -la "$output_dir"/*.tar.* 2>/dev/null || ls -la "$output_dir"/*.tar.bz2 2>/dev/null || true
    fi
}

build_linux_debug() {
    log_info "Building STGR Browser for Linux (debug)..."
    check_vaapi
    cd "$STGR_SOURCE_DIR"
    export MOZ_DEBUG=1
    export MOZ_BUILD_DATE=20260701
    ./mach build
    cd "$PROJECT_ROOT"
    log_success "Linux debug build complete!"
}

run_linux() {
    cd "$STGR_SOURCE_DIR"
    ./mach run
    cd "$PROJECT_ROOT"
}

# Main
case "${1:-help}" in
    deps)          install_deps ;;
    build)         build_linux_release ;;
    build-debug)   build_linux_debug ;;
    run)           run_linux ;;
    vaapi-check)   check_vaapi ;;
    vaapi-install) install_vaapi_driver ;;
    help|*)
        echo "STGR Browser - Linux Build Script"
        echo ""
        echo "Usage: ./scripts/build-linux.sh [command]"
        echo ""
        echo "Commands:"
        echo "  deps              Install build dependencies + VA-API check"
        echo "  build             Build STGR Browser for Linux (release)"
        echo "  build-debug       Build STGR Browser for Linux (debug)"
        echo "  run               Run STGR Browser"
        echo "  vaapi-check       Check VA-API/hardware video decode status"
        echo "  vaapi-install     Install the recommended VA-API driver"
        echo ""
        echo "Example:"
        echo "  ./scripts/build-linux.sh build        # Full build"
        echo "  ./scripts/build-linux.sh vaapi-check  # Check video decode"
        ;;
esac
