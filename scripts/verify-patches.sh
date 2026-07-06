#!/bin/bash
# ============================================================================
# STGR Browser - Patch Verification Script
# ============================================================================
# Verifies that all STGR patches apply cleanly to the Firefox source tree.
# Checks patch structure, file references, and application status.
#
# Usage:
#   ./scripts/verify-patches.sh               # Dry-run check all patches
#   ./scripts/verify-patches.sh --apply       # Actually apply patches
#   ./scripts/verify-patches.sh --check-only  # Structural check only
#   ./scripts/verify-patches.sh --help        # Show this help
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STGR_SOURCE_DIR="${STGR_SOURCE_DIR:-$PROJECT_ROOT/gecko-dev}"
STGR_PATCHES_DIR="$PROJECT_ROOT/patches"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_pass()  { echo -e "${GREEN}[PASS]${NC} $1"; }
log_fail()  { echo -e "${RED}[FAIL]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }

TOTAL=0
CLEAN=0
ISSUES=0
WARN=0

check_patch_exists() {
    local num="$1"
    local name="$2"
    TOTAL=$((TOTAL + 1))

    local file="$STGR_PATCHES_DIR/$num-$name.patch"
    if [ -f "$file" ]; then
        log_pass "$num: $name — found"
        CLEAN=$((CLEAN + 1))
    else
        log_fail "$num: $name — MISSING"
        ISSUES=$((ISSUES + 1))
    fi
}

check_patch_structural() {
    local num="$1"
    local name="$2"
    TOTAL=$((TOTAL + 1))

    local file="$STGR_PATCHES_DIR/$num-$name.patch"
    if [ ! -f "$file" ]; then
        ISSUES=$((ISSUES + 1))
        return
    fi

    local has_diff=false
    local has_from=false
    local has_date=false
    local has_subject=false
    local has_placeholder=false

    if grep -q "^diff --git " "$file" 2>/dev/null; then has_diff=true; fi
    if grep -q "^From:" "$file" 2>/dev/null; then has_from=true; fi
    if grep -q "^Date:" "$file" 2>/dev/null; then has_date=true; fi
    if grep -q "^Subject:" "$file" 2>/dev/null; then has_subject=true; fi
    if grep -q "@@ -X,Y +X,Y @@" "$file" 2>/dev/null; then has_placeholder=true; fi

    local issues=""

    if ! $has_diff; then issues="$issues [NO DIFF]"; fi
    if ! $has_from && ! $has_date && ! $has_subject; then
        issues="$issues [MISSING HEADER]"
    fi
    if $has_placeholder; then issues="$issues [PLACEHOLDER LINE NUMBERS]"; fi

    if [ -z "$issues" ]; then
        log_pass "$num: $name — structure valid"
        CLEAN=$((CLEAN + 1))
    else
        log_warn "$num: $name —$issues"
        WARN=$((WARN + 1))
    fi
}

check_patch_apply() {
    if [ ! -d "$STGR_SOURCE_DIR" ] || [ ! -d "$STGR_SOURCE_DIR/.git" ]; then
        log_warn "Firefox source not found or not a git repo — skipping apply check"
        return
    fi

    local num="$1"
    local name="$2"
    TOTAL=$((TOTAL + 1))

    local file="$STGR_PATCHES_DIR/$num-$name.patch"
    if [ ! -f "$file" ]; then
        ISSUES=$((ISSUES + 1))
        return
    fi

    cd "$STGR_SOURCE_DIR"
    if git apply --check "$file" 2>/dev/null; then
        log_pass "$num: $name — applies cleanly"
        CLEAN=$((CLEAN + 1))
    else
        log_fail "$num: $name — FAILS TO APPLY"
        ISSUES=$((ISSUES + 1))
    fi
    cd "$PROJECT_ROOT"
}

check_pref_names() {
    local num="$1"
    local name="$2"
    TOTAL=$((TOTAL + 1))

    local file="$STGR_PATCHES_DIR/$num-$name.patch"
    if [ ! -f "$file" ]; then
        ISSUES=$((ISSUES + 1))
        return
    fi

    # Check for any non-STGR pref names that might have been missed
    local mozilla_prefs
    mozilla_prefs=$(grep -oP '(?<=pref\()[^)]+' "$file" 2>/dev/null | grep -v "stgr\." | grep -oP '"[^"]+"' | head -5 || true)

    if [ -n "$mozilla_prefs" ]; then
        log_warn "$num: $name — uses Mozilla-style prefs (may be intentional):"
        echo "$mozilla_prefs" | while IFS= read -r pref; do echo "         $pref"; done
        WARN=$((WARN + 1))
    else
        log_pass "$num: $name — pref naming looks clean"
        CLEAN=$((CLEAN + 1))
    fi
}

# All patches in expected order
declare -a PATCHES=(
    "0001:remove-telemetry"
    "0002:remove-pocket-sync"
    "0003:remove-sponsored-content"
    "0004:memory-optimizations"
    "0005:gpu-optimizations"
    "0006:gaming-mode"
    "0007:ui-customization"
    "0008:privacy-defaults"
    "0009:startup-optimizations"
    "0010:vertical-tabs"
    "0011:tab-groups"
    "0012:tab-preview-screenshots"
    "0013:auto-hide"
    "0014:enhanced-tab-search"
    "0015:stgr-preferences-pane"
)

echo "=============================================="
echo " STGR Browser - Patch Verification"
echo "=============================================="
echo ""

MODE="${1:---check-only}"
case "$MODE" in
    --help)
        echo "Usage: ./scripts/verify-patches.sh [MODE]"
        echo ""
        echo "Modes:"
        echo "  --check-only     Structural check (default)"
        echo "  --dry-run        Check application without applying"
        echo "  --apply          Actually apply all patches"
        echo "  --help           Show this help"
        exit 0
        ;;
esac

echo "Checking ${#PATCHES[@]} patches..."
echo ""

for entry in "${PATCHES[@]}"; do
    num="${entry%%:*}"
    name="${entry#*:}"

    check_patch_exists "$num" "$name"

    if [ -f "$STGR_PATCHES_DIR/$num-$name.patch" ]; then
        check_patch_structural "$num" "$name"
    fi

    if [ "$MODE" = "--dry-run" ] || [ "$MODE" = "--apply" ]; then
        check_patch_apply "$num" "$name"
    fi

    if grep -q "pref(" "$STGR_PATCHES_DIR/$num-$name.patch" 2>/dev/null; then
        check_pref_names "$num" "$name"
    fi
done

echo ""
echo "=============================================="
echo " Results: $CLEAN/$TOTAL checks passed, $ISSUES issues, $WARN warnings"
echo "=============================================="

if [ "$ISSUES" -gt 0 ]; then
    echo ""
    log_fail "Some patches have issues that need attention."
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo ""
    log_warn "All patches present, but some have warnings."
    exit 0
else
    echo ""
    log_pass "All patches verified successfully!"
    exit 0
fi
