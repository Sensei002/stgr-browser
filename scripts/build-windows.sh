#!/bin/bash
# ============================================================================
# STGR Browser - Windows Build Script
# ============================================================================
# Builds STGR Browser for Windows using Mozilla's toolchain.
#
# Prerequisites:
#   - Visual Studio 2022 (Community/Professional/Enterprise)
#   - Windows 10 SDK (10.0.20348.0 or later)
#   - MozillaBuild (https://firefox-source-docs.mozilla.org/setup/windows_build.html)
#   - Rust toolchain via rustup
#   - Node.js 18+
#   - Python 3.8+
#
# Windows-specific notes:
#   - Must be run from MozillaBuild environment (start-shell.bat)
#   - Uses clang-cl as the default compiler
#   - DirectX 11/12 and Vulkan support enabled
#   - D2D and D3D hardware acceleration enabled
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

check_windows_prereqs() {
    log_info "Checking Windows prerequisites..."

    # Check for VS 2022
    VSWHERE="${PROGRAMFILES(X86)}//Microsoft Visual Studio//Installer//vswhere.exe"
    if [ -f "$VSWHERE" ]; then
        VS_PATH=$("$VSWHERE" -latest -property installationPath 2>/dev/null || echo "")
        if [ -n "$VS_PATH" ]; then
            log_success "Visual Studio found: $VS_PATH"
        else
            log_warn "Visual Studio not detected via vswhere"
        fi
    fi

    # Check for Windows SDK
    if [ -d "C:/Program Files (x86)/Windows Kits/10" ]; then
        log_success "Windows SDK found"
    else
        log_warn "Windows SDK not detected"
    fi

    # Check Rust with Windows target
    if rustup target list --installed | grep -q "x86_64-pc-windows-msvc"; then
        log_success "Rust Windows MSVC target found"
    else
        log_warn "Installing Rust Windows MSVC target..."
        rustup target add x86_64-pc-windows-msvc
    fi
}

build_windows_release() {
    log_info "Building STGR Browser for Windows (release)..."

    cd "$STGR_SOURCE_DIR"

    # Export Windows-specific environment
    export MOZ_BUILD_DATE=20260701
    export MOZ_AUTOMATION=1
    export PATH="/c/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.40.33807/bin/Hostx64/x64:$PATH"

    # Configure with Windows-optimized mozconfig
    export MOZCONFIG="$PROJECT_ROOT/config/mozconfig"

    # Build
    ./mach build

    # Create installer
    ./mach build installer

    cd "$PROJECT_ROOT"
    log_success "Windows build complete!"
    
    # Show output
    local output_dir="$STGR_SOURCE_DIR/obj-build-stgr/dist"
    if [ -d "$output_dir" ]; then
        log_info "Installer available at:"
        ls -la "$output_dir"/*.exe 2>/dev/null || ls -la "$output_dir"/*.msi 2>/dev/null || true
    fi
}

build_windows_debug() {
    log_info "Building STGR Browser for Windows (debug)..."

    cd "$STGR_SOURCE_DIR"

    export MOZ_DEBUG=1
    export MOZ_BUILD_DATE=20260701

    ./mach build

    cd "$PROJECT_ROOT"
    log_success "Windows debug build complete!"
}

run_windows() {
    log_info "Running STGR Browser..."
    cd "$STGR_SOURCE_DIR"
    ./mach run
    cd "$PROJECT_ROOT"
}

# Main
case "${1:-help}" in
    build)       check_windows_prereqs && build_windows_release ;;
    build-debug) check_windows_prereqs && build_windows_debug ;;
    run)         run_windows ;;
    help|*)
        echo "STGR Browser - Windows Build Script"
        echo ""
        echo "Usage: ./scripts/build-windows.sh [command]"
        echo ""
        echo "Commands:"
        echo "  build          Build STGR Browser for Windows (release)"
        echo "  build-debug    Build STGR Browser for Windows (debug)"
        echo "  run            Run STGR Browser"
        echo ""
        echo "Must be run from MozillaBuild shell."
        ;;
esac
