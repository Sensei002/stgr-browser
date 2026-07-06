#!/bin/bash
# ============================================================================
# STGR Browser - Patch Application Script
# ============================================================================
# Applies all STGR optimization patches to the Firefox source tree.
#
# Usage: ./scripts/apply-patches.sh [--install]
#   --install: Also copies STGR source files into the Firefox tree
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STGR_SOURCE_DIR="${STGR_SOURCE_DIR:-$PROJECT_ROOT/gecko-dev}"
STGR_PATCHES_DIR="$PROJECT_ROOT/patches"
STGR_CONFIG_DIR="$PROJECT_ROOT/config"

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Validate environment
validate() {
    if [ ! -d "$STGR_SOURCE_DIR" ]; then
        log_error "Firefox source directory not found: $STGR_SOURCE_DIR"
        log_error "Run ./scripts/setup.sh first."
        exit 1
    fi

    if [ ! -d "$STGR_PATCHES_DIR" ]; then
        log_error "Patches directory not found: $STGR_PATCHES_DIR"
        exit 1
    fi

    # Check if it's a git repository
    if [ ! -d "$STGR_SOURCE_DIR/.git" ]; then
        log_warn "Firefox source is not a git repository. Patches will be applied with git apply."
        log_warn "Use --install flag if you want to copy files instead."
    fi
}

# Apply patches in order
apply_patches() {
    log_info "Applying STGR patches to Firefox source..."
    
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
    local applied=0
    local failed=0

    for patch in "${patches[@]}"; do
        local patch_path="$STGR_PATCHES_DIR/$patch"
        if [ -f "$patch_path" ]; then
            log_info "Applying: $patch..."
            if git apply --check "$patch_path" 2>/dev/null; then
                git apply "$patch_path"
                log_success "  ✓ $patch"
                applied=$((applied + 1))
            else
                log_warn "  ✗ $patch (conflicts detected, applying with --reject)"
                log_warn "  Check $STGR_SOURCE_DIR for .rej files"
                git apply --reject "$patch_path" 2>/dev/null || true
                failed=$((failed + 1))
            fi
        else
            log_warn "  - $patch (not found)"
        fi
    done

    cd "$PROJECT_ROOT"
    
    echo ""
    log_info "Patch summary: $applied applied, $failed with issues"
    if [ $failed -gt 0 ]; then
        log_warn "Some patches had conflicts. Manual resolution may be required."
        log_warn "Check rejected files (*.rej) in the source tree."
    fi
}

# Install STGR source files directly
install_source_files() {
    log_info "Installing STGR source files into Firefox tree..."

    # Create STGR directories
    mkdir -p "$STGR_SOURCE_DIR/stgr"
    mkdir -p "$STGR_SOURCE_DIR/stgr/branding"
    mkdir -p "$STGR_SOURCE_DIR/stgr/components"
    mkdir -p "$STGR_SOURCE_DIR/stgr/themes"
    mkdir -p "$STGR_SOURCE_DIR/stgr/locales/en-US"

    # Copy branding
    log_info "Copying branding assets..."
    cp -r "$PROJECT_ROOT/branding/"* "$STGR_SOURCE_DIR/stgr/branding/" 2>/dev/null || true

    # Copy configuration — use platform-specific mozconfig
    log_info "Copying configuration files..."
    local platform=$(detect_platform)
    local mozconfig_src="$PROJECT_ROOT/config/mozconfig-$platform"
    if [ ! -f "$mozconfig_src" ]; then
        mozconfig_src="$PROJECT_ROOT/config/mozconfig"
    fi
    cp "$mozconfig_src" "$STGR_SOURCE_DIR/mozconfig" 2>/dev/null || true
    # Also copy platform files so the wrapper's . inclusion works
    mkdir -p "$STGR_SOURCE_DIR/config"
    for pf in windows linux macos; do
        if [ -f "$PROJECT_ROOT/config/mozconfig-$pf" ]; then
            cp "$PROJECT_ROOT/config/mozconfig-$pf" "$STGR_SOURCE_DIR/config/mozconfig-$pf" 2>/dev/null || true
        fi
    done
    cp "$PROJECT_ROOT/config/stgr-prefs.js" "$STGR_SOURCE_DIR/stgr/stgr-prefs.js" 2>/dev/null || true

    # Create STGR build configuration
    cat > "$STGR_SOURCE_DIR/stgr/STGRBuildConfig.h" << 'EOF'
#ifndef STGR_BUILD_CONFIG_H
#define STGR_BUILD_CONFIG_H

#define STGR_APP_NAME "STGR Browser"
#define STGR_APP_VENDOR "STGR"
#define STGR_APP_VERSION "1.0.0"
#define STGR_BUILD_ID "20260701"
#define STGR_UA_VENDOR "STGR"

#endif // STGR_BUILD_CONFIG_H
EOF

    log_success "Source files installed!"
}

# Main
validate

INSTALL_FILES=false
for arg in "$@"; do
    case "$arg" in
        --install) INSTALL_FILES=true ;;
    esac
done

if $INSTALL_FILES; then
    install_source_files
fi

apply_patches

if $INSTALL_FILES; then
    echo ""
    log_success "Patches applied and source files installed!"
    echo ""
    echo "Next steps:"
    echo "  1. cd $STGR_SOURCE_DIR"
    echo "  2. Review any rejected patches (*.rej)"
    echo "  3. ./mach build"
    echo "  4. ./mach run"
else
    echo ""
    log_success "Patches applied!"
    echo ""
    echo "Tip: Use --install flag to also copy STGR source files and branding."
fi
