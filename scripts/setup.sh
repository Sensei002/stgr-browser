#!/bin/bash
# ============================================================================
# STGR Browser - Environment Setup Script
# ============================================================================
# This script clones the Firefox source code and prepares the build environment
# for STGR Browser development.
#
# Prerequisites:
#   - Git
#   - Mozilla build prerequisites (see: https://firefox-source-docs.mozilla.org/setup/)
#   - Rust toolchain (rustup)
#   - Node.js 18+
#   - Python 3.8+
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
FIREFOX_REPO="${FIREFOX_REPO:-https://github.com/mozilla/gecko-dev.git}"
FIREFOX_BRANCH="${FIREFOX_BRANCH:-RELEASE_BASE_20250701}"
STGR_SOURCE_DIR="${STGR_SOURCE_DIR:-$PROJECT_ROOT/gecko-dev}"
STGR_PATCHES_DIR="$PROJECT_ROOT/patches"
STGR_CONFIG_DIR="$PROJECT_ROOT/config"
STGR_BRANDING_DIR="$PROJECT_ROOT/branding"

# Detect current OS platform
detect_platform() {
    local uname_s="$(uname -s)"
    case "$uname_s" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

PLATFORM=$(detect_platform)

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    log_info "Detected platform: $PLATFORM"

    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
    log_success "Git found: $(git --version)"

    # Check Rust
    if ! command -v rustc &> /dev/null; then
        log_error "Rust is not installed. Install via: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        exit 1
    fi
    log_success "Rust found: $(rustc --version)"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed."
        exit 1
    fi
    log_success "Node.js found: $(node --version)"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed."
        exit 1
    fi
    log_success "Python found: $(python3 --version)"

    # Check Mozilla bootstrap
    if ! command -v mach &> /dev/null && [ ! -f "$STGR_SOURCE_DIR/mach" ]; then
        log_warn "Mozilla mach not found. It will be set up after cloning."
    fi
}

# Clone Firefox source
clone_firefox() {
    if [ -d "$STGR_SOURCE_DIR" ]; then
        log_warn "Firefox source directory already exists at $STGR_SOURCE_DIR"
        read -p "Do you want to re-clone? (y/N): " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            log_info "Removing existing directory..."
            rm -rf "$STGR_SOURCE_DIR"
        else
            log_info "Using existing source directory."
            return
        fi
    fi

    log_info "Cloning Firefox source from $FIREFOX_REPO..."
    log_info "Branch: $FIREFOX_BRANCH"
    log_warn "This may take a while (10-30 minutes depending on connection)..."

    git clone --depth 1 --branch "$FIREFOX_BRANCH" "$FIREFOX_REPO" "$STGR_SOURCE_DIR"

    if [ $? -ne 0 ]; then
        log_error "Failed to clone Firefox source."
        exit 1
    fi

    log_success "Firefox source cloned successfully."
}

# Create STGR source directory structure inside gecko-dev
setup_stgr_source() {
    log_info "Setting up STGR Browser source directories..."

    # Create STGR branding directory within the Firefox source tree
    mkdir -p "$STGR_SOURCE_DIR/stgr/branding"
    mkdir -p "$STGR_SOURCE_DIR/stgr/components"
    mkdir -p "$STGR_SOURCE_DIR/stgr/locales"
    mkdir -p "$STGR_SOURCE_DIR/stgr/themes"

    # Copy STGR branding assets to Firefox source tree
    log_info "Copying STGR branding assets..."
    cp -r "$STGR_BRANDING_DIR/"* "$STGR_SOURCE_DIR/stgr/branding/"

    log_success "STGR source directories created."
}

# Apply all STGR patches
apply_patches() {
    log_info "Applying STGR optimization patches..."
    
    local patches=(
        "0001-remove-telemetry.patch"
        "0002-remove-pocket-sync.patch"
        "0003-remove-sponsored-content.patch"
        "0004-memory-optimizations.patch"
        "0005-gpu-optimizations.patch"
        "0006-gaming-mode.patch"
        "0007-ui-customization.patch"
        "0008-privacy-defaults.patch"
        "0009-startup-optimizations.patch"
        "0010-vertical-tabs.patch"
        "0011-tab-groups.patch"
        "0012-tab-preview-screenshots.patch"
        "0013-auto-hide.patch"
        "0014-enhanced-tab-search.patch"
        "0015-stgr-preferences-pane.patch"
    )

    cd "$STGR_SOURCE_DIR"

    for patch in "${patches[@]}"; do
        local patch_path="$STGR_PATCHES_DIR/$patch"
        if [ -f "$patch_path" ]; then
            log_info "Applying $patch..."
            if git apply "$patch_path" 2>/dev/null; then
                log_success "  Applied: $patch"
            else
                log_warn "  Could not apply $patch (may need manual resolution)"
                log_warn "  See: $patch_path"
            fi
        else
            log_warn "  Patch not found: $patch"
        fi
    done

    cd "$PROJECT_ROOT"
    log_success "Patch application complete."
}

# Configure STGR build for the detected platform
configure_build() {
    log_info "Configuring STGR Browser build for $PLATFORM..."

    # Select the platform-specific mozconfig
    local mozconfig_src="$STGR_CONFIG_DIR/mozconfig-$PLATFORM"
    if [ ! -f "$mozconfig_src" ]; then
        log_warn "Platform-specific mozconfig not found: $mozconfig_src"
        log_warn "Falling back to generic mozconfig wrapper."
        mozconfig_src="$STGR_CONFIG_DIR/mozconfig"
    fi

    # Copy the mozconfig (the smart wrapper detects OS at build time; we also
    # copy the platform files it includes so relative paths resolve)
    cp "$mozconfig_src" "$STGR_SOURCE_DIR/mozconfig"

    # Also copy platform-specific files so the wrapper's . inclusion works
    mkdir -p "$STGR_SOURCE_DIR/config"
    for pf in windows linux macos; do
        if [ -f "$STGR_CONFIG_DIR/mozconfig-$pf" ]; then
            cp "$STGR_CONFIG_DIR/mozconfig-$pf" "$STGR_SOURCE_DIR/config/mozconfig-$pf" 2>/dev/null || true
        fi
    done

    # Copy STGR preferences
    cp "$STGR_CONFIG_DIR/stgr-prefs.js" "$STGR_SOURCE_DIR/stgr/stgr-prefs.js"

    log_success "Build configuration applied (platform: $PLATFORM)."
    log_info "mozconfig: $mozconfig_src -> $STGR_SOURCE_DIR/mozconfig"
}

# Run Mozilla bootstrap
run_bootstrap() {
    log_info "Running Mozilla bootstrap to install build dependencies..."
    log_warn "This requires sudo/administrator privileges."
    
    cd "$STGR_SOURCE_DIR"
    
    if [ -f "./mach" ]; then
        if command -v sudo &> /dev/null; then
            sudo ./mach bootstrap --application-choice=browser
        else
            log_warn "sudo not available. Running mach bootstrap without..."
            ./mach bootstrap --application-choice=browser
        fi
    else
        log_error "mach not found. Please run ./mach bootstrap manually."
        exit 1
    fi

    cd "$PROJECT_ROOT"
    log_success "Bootstrap complete."
}

# Main execution
main() {
    echo "============================================="
    echo " STGR Browser - Development Setup"
    echo "============================================="
    echo ""

    check_prerequisites
    clone_firefox
    setup_stgr_source
    apply_patches
    configure_build
    run_bootstrap

    echo ""
    echo "============================================="
    log_success "STGR Browser environment is ready!"
    echo "============================================="
    echo ""
    echo "Next steps:"
    echo "  1. cd $STGR_SOURCE_DIR"
    echo "  2. ./mach build"
    echo "  3. ./mach run"
    echo ""
    echo "For more details, see: docs/BUILD.md"
}

main
