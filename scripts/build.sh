#!/bin/bash
# ============================================================================
# STGR Browser - Unified Build Script
# ============================================================================
# Usage: ./scripts/build.sh [command]
#
# Commands:
#   build          Build STGR Browser (release)
#   build-debug    Build STGR Browser (debug)
#   build-clean    Clean build
#   run            Build and run STGR Browser
#   package        Create installer package
#   test           Run tests
#   lint           Run linters
#   clean          Clean build artifacts
#   help           Show this help message
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

# Detect OS platform
detect_platform() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

PLATFORM=$(detect_platform)

# Set platform-appropriate mozconfig (setup.sh copies the right one)
export MOZCONFIG="$PROJECT_ROOT/config/mozconfig"

# Check if source exists
check_source() {
    if [ ! -d "$STGR_SOURCE_DIR" ]; then
        log_error "Firefox source not found at $STGR_SOURCE_DIR"
        log_error "Run ./scripts/setup.sh first to clone Firefox and set up the build environment."
        exit 1
    fi
    if [ ! -f "$STGR_SOURCE_DIR/mach" ]; then
        log_error "Mozilla mach not found in source directory."
        exit 1
    fi
    log_info "Building for platform: $PLATFORM"
    local mozconfig_target="$STGR_SOURCE_DIR/mozconfig"
    if [ -f "$mozconfig_target" ]; then
        local mozconfig_origin
        mozconfig_origin=$(head -5 "$mozconfig_target" | grep -i "STGR Browser" | head -1 || echo "$mozconfig_target")
        log_info "Using mozconfig: $mozconfig_target"
    else
        log_warn "No mozconfig found at $mozconfig_target — copying default..."
        cp "$PROJECT_ROOT/config/mozconfig-$PLATFORM" "$mozconfig_target" 2>/dev/null || \
        cp "$PROJECT_ROOT/config/mozconfig" "$mozconfig_target" 2>/dev/null || true
    fi
}

# Build release
build_release() {
    check_source
    log_info "Building STGR Browser for $PLATFORM (release)..."
    cd "$STGR_SOURCE_DIR"
    ./mach build
    cd "$PROJECT_ROOT"
    log_success "Build complete for $PLATFORM!"
}

# Build debug
build_debug() {
    check_source
    log_info "Building STGR Browser for $PLATFORM (debug)..."
    cd "$STGR_SOURCE_DIR"
    export MOZ_DEBUG=1
    ./mach build
    cd "$PROJECT_ROOT"
    log_success "Debug build complete for $PLATFORM!"
}

# Clean build
build_clean() {
    check_source
    log_info "Performing clean build of STGR Browser for $PLATFORM..."
    cd "$STGR_SOURCE_DIR"
    ./mach clobber
    ./mach build
    cd "$PROJECT_ROOT"
    log_success "Clean build complete for $PLATFORM!"
}

# Build and run
build_run() {
    check_source
    log_info "Building and running STGR Browser for $PLATFORM..."
    cd "$STGR_SOURCE_DIR"
    ./mach run
    cd "$PROJECT_ROOT"
}

# Package installer
package_installer() {
    check_source
    log_info "Packaging STGR Browser installer for $PLATFORM..."
    
    cd "$STGR_SOURCE_DIR"
    
    case "$PLATFORM" in
        windows)
            ./mach build installer
            log_info "Installer created in: $STGR_SOURCE_DIR/obj-build-stgr/dist/"
            ;;
        linux)
            ./mach build package
            ./mach build installer
            log_info "Package created in: $STGR_SOURCE_DIR/obj-build-stgr/dist/"
            ;;
        macos)
            ./mach build package
            ./mach build dmg
            log_info "DMG created in: $STGR_SOURCE_DIR/obj-build-stgr/dist/"
            ;;
        *)
            log_error "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac
    
    cd "$PROJECT_ROOT"
    log_success "Packaging complete for $PLATFORM!"
}

# Run tests
run_tests() {
    check_source
    log_info "Running STGR Browser tests on $PLATFORM..."
    cd "$STGR_SOURCE_DIR"
    ./mach test
    cd "$PROJECT_ROOT"
    log_success "Tests complete!"
}

# Run linters
run_lint() {
    check_source
    log_info "Running linters..."
    cd "$STGR_SOURCE_DIR"
    ./mach lint
    ./mach clang-format
    cd "$PROJECT_ROOT"
    log_success "Linting complete!"
}

# Clean everything
clean_all() {
    log_info "Cleaning build artifacts..."
    if [ -d "$STGR_SOURCE_DIR" ]; then
        cd "$STGR_SOURCE_DIR"
        if [ -f "./mach" ]; then
            ./mach clobber 2>/dev/null || true
        fi
        cd "$PROJECT_ROOT"
    fi
    log_success "Clean complete!"
}

# Show help
show_help() {
    echo "STGR Browser - Build Script"
    echo ""
    echo "Usage: ./scripts/build.sh [command]"
    echo "  Current platform: $PLATFORM"
    echo ""
    echo "Commands:"
    echo "  build          Build STGR Browser (release)"
    echo "  build-debug    Build STGR Browser (debug)"
    echo "  build-clean    Clean build"
    echo "  run            Build and run STGR Browser"
    echo "  package        Create installer package"
    echo "  test           Run tests"
    echo "  lint           Run linters"
    echo "  clean          Clean build artifacts"
    echo "  help           Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  STGR_SOURCE_DIR    Path to Firefox source (default: ./gecko-dev)"
    echo "  MOZ_DEBUG          Set to 1 for debug build"
    echo "  MOZCONFIG          Path to mozconfig (auto-detected by platform)"
    echo ""
    echo "Examples:"
    echo "  ./scripts/build.sh build          # Release build"
    echo "  ./scripts/build.sh run            # Build and run"
    echo "  ./scripts/build.sh package        # Create installer"
}

# Main
case "${1:-help}" in
    build)        build_release ;;
    build-debug)  build_debug ;;
    build-clean)  build_clean ;;
    run)          build_run ;;
    package)      package_installer ;;
    test)         run_tests ;;
    lint)         run_lint ;;
    clean)        clean_all ;;
    help|*)       show_help ;;
esac
