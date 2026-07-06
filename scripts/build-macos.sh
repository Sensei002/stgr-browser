#!/bin/bash
# ============================================================================
# STGR Browser - macOS Build Script
# ============================================================================
# Builds STGR Browser for macOS.
#
# Prerequisites:
#   - Xcode 15+ (from Mac App Store)
#   - Command Line Tools: xcode-select --install
#   - Homebrew: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
#   - Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
#   - Node.js 18+: brew install node
#   - Python 3: brew install python
#
# macOS-specific features:
#   - Metal graphics API support
#   - Apple Silicon (ARM64) native builds
#   - Universal binary (x86_64 + arm64) support
#   - macOS native UI toolkit (Cocoa)
#   - Hardware-accelerated video decoding (VDA/VTB)
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
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check macOS prerequisites
check_macos_prereqs() {
    log_info "Checking macOS prerequisites..."

    # Check Xcode
    if xcode-select -p &>/dev/null; then
        log_success "Xcode found: $(xcode-select -p)"
    else
        log_error "Xcode not found. Install from Mac App Store."
        exit 1
    fi

    # Check Xcode version
    if command -v xcodebuild &>/dev/null; then
        log_info "Xcode version: $(xcodebuild -version | head -1)"
    fi

    # Check Rosetta 2 on Apple Silicon
    if [[ $(uname -m) == "arm64" ]]; then
        if sysctl -n sysctl.proc_translated 2>/dev/null; then
            log_success "Apple Silicon detected - native ARM64 build"
        fi
    fi

    # Check Homebrew
    if command -v brew &>/dev/null; then
        log_success "Homebrew found"
    else
        log_warn "Homebrew not found. Install from: https://brew.sh"
    fi
}

# Install macOS dependencies
install_macos_deps() {
    log_info "Installing macOS build dependencies..."

    # Install via Homebrew
    brew update
    brew install \
        rustup-init \
        node \
        python \
        pkg-config \
        make \
        autoconf \
        autoconf-archive \
        automake \
        libtool \
        yasm \
        nasm \
        ccache \
        llvm@16

    # Install Rust
    if ! command -v rustc &>/dev/null; then
        rustup-init -y
        source "$HOME/.cargo/env"
    fi

    # Add macOS targets
    rustup target add x86_64-apple-darwin
    if [[ $(uname -m) == "arm64" ]]; then
        rustup target add aarch64-apple-darwin
    fi

    log_success "macOS dependencies installed!"
}

build_macos_release() {
    log_info "Building STGR Browser for macOS (release)..."

    cd "$STGR_SOURCE_DIR"

    export MOZ_BUILD_DATE=20260701
    export MOZ_AUTOMATION=1
    export MOZCONFIG="$PROJECT_ROOT/config/mozconfig"

    # macOS-specific build flags
    export MACOSX_DEPLOYMENT_TARGET=11.0
    export MOZ_MACBUNDLE_NAME="STGR Browser"

    ./mach build
    ./mach build package
    ./mach build dmg

    cd "$PROJECT_ROOT"
    log_success "macOS build complete!"
    
    local output_dir="$STGR_SOURCE_DIR/obj-build-stgr/dist"
    if [ -d "$output_dir" ]; then
        log_info "DMG available at:"
        ls -la "$output_dir"/*.dmg 2>/dev/null || true
    fi
}

build_macos_debug() {
    log_info "Building STGR Browser for macOS (debug)..."
    cd "$STGR_SOURCE_DIR"
    export MOZ_DEBUG=1
    export MOZ_BUILD_DATE=20260701
    ./mach build
    cd "$PROJECT_ROOT"
    log_success "macOS debug build complete!"
}

build_macos_universal() {
    log_info "Building STGR Browser for macOS (universal binary)..."
    cd "$STGR_SOURCE_DIR"
    export MOZ_BUILD_DATE=20260701
    export MOZ_AUTOMATION=1
    export MOZCONFIG="$PROJECT_ROOT/config/mozconfig"
    export MOZ_UNIVERSAL_BINARY=1
    ./mach build
    ./mach build package
    ./mach build dmg
    cd "$PROJECT_ROOT"
    log_success "Universal build complete!"
}

run_macos() {
    cd "$STGR_SOURCE_DIR"
    ./mach run
    cd "$PROJECT_ROOT"
}

# Main
case "${1:-help}" in
    deps)         check_macos_prereqs && install_macos_deps ;;
    build)        check_macos_prereqs && build_macos_release ;;
    build-debug)  check_macos_prereqs && build_macos_debug ;;
    build-universal) check_macos_prereqs && build_macos_universal ;;
    run)          run_macos ;;
    help|*)
        echo "STGR Browser - macOS Build Script"
        echo ""
        echo "Usage: ./scripts/build-macos.sh [command]"
        echo ""
        echo "Commands:"
        echo "  deps              Install build dependencies"
        echo "  build             Build STGR Browser for macOS (release)"
        echo "  build-debug       Build STGR Browser for macOS (debug)"
        echo "  build-universal   Build universal binary (x86_64 + arm64)"
        echo "  run               Run STGR Browser"
        ;;
esac
