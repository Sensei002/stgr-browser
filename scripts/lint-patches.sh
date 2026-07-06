#!/bin/bash
# ============================================================================
# STGR Browser - Patch Linting Script
# ============================================================================
# Checks for consistency issues across all STGR patches:
#   - Verifies all STGR preferences use the "stgr." prefix
#   - Checks for duplicate preference definitions
#   - Validates patch numbering and ordering
#   - Reports any leftover Mozilla references
#
# Usage: ./scripts/lint-patches.sh
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STGR_PATCHES_DIR="$PROJECT_ROOT/patches"
STGR_CONFIG_DIR="$PROJECT_ROOT/config"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_pass()  { echo -e "${GREEN}[PASS]${NC} $1"; }
log_fail()  { echo -e "${RED}[FAIL]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }

ERRORS=0
WARNINGS=0
CHECKS=0

echo "=============================================="
echo " STGR Browser - Patch Linting"
echo "=============================================="
echo ""

# Check 1: All patches exist in order
CHECKS=$((CHECKS + 1))
log_info "Check 1: Patch numbering and ordering..."
missing_patches=false
for i in $(seq -f '%04g' 1 15); do
    match=$(ls "$STGR_PATCHES_DIR/${i}-"*.patch 2>/dev/null || true)
    if [ -z "$match" ]; then
        log_fail "  Missing patch: $i-*.patch"
        missing_patches=true
        ERRORS=$((ERRORS + 1))
    fi
done
if [ "$missing_patches" = false ]; then
    log_pass "  All 15 patches present and correctly numbered"
fi
echo ""

# Check 2: Duplicate pref definitions across patches
CHECKS=$((CHECKS + 1))
log_info "Check 2: Duplicate preference definitions..."
ALL_PREFS=$(grep -rohP '(?<=pref\(")[^"]+' "$STGR_PATCHES_DIR" 2>/dev/null | sort || true)
DUPS=$(echo "$ALL_PREFS" | uniq -d || true)
if [ -n "$DUPS" ]; then
    log_warn "  Duplicate preference(s) found across patches:"
    echo "$DUPS" | while IFS= read -r pref; do
        locations=$(grep -rl "pref(\"$pref" "$STGR_PATCHES_DIR" 2>/dev/null | tr '\n' ' ' || true)
        echo "    $pref → $locations"
    done
    WARNINGS=$((WARNINGS + 1))
else
    log_pass "  No duplicate prefs found across patches"
fi
echo ""

# Check 3: STGR pref prefix consistency
CHECKS=$((CHECKS + 1))
log_info "Check 3: STGR preference prefix (stgr.)..."
STGR_IN_PATCHES=$(grep -rohP '(?<=pref\(")stgr\.[^"]+' "$STGR_PATCHES_DIR" 2>/dev/null | sort -u || true)
STGR_IN_CONFIG=$(grep -rohP '(?<=pref\(")stgr\.[^"]+' "$STGR_CONFIG_DIR/stgr-prefs.js" 2>/dev/null | sort -u || true)

# Check all STGR prefs in patches are defined in config
MISSING_IN_CONFIG=false
while IFS= read -r pref; do
    if [ -n "$pref" ]; then
        if ! echo "$STGR_IN_CONFIG" | grep -qF "$pref"; then
            log_warn "  Pref in patches but NOT in config: $pref"
            MISSING_IN_CONFIG=true
        fi
    fi
done <<< "$STGR_IN_PATCHES"
if ! $MISSING_IN_CONFIG; then
    log_pass "  All patch prefs are defined in stgr-prefs.js"
else
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check 4: Leftover Mozilla/Firefox references that should be STGR
CHECKS=$((CHECKS + 1))
log_info "Check 4: Leftover Mozilla/Firefox branding references..."
branding_issues=false

# Check for common leftover strings in patches (only + lines — STGR's additions, not context lines)
while IFS= read -r line; do
    case "$line" in
        *"Mozilla Firefox"*|*"Firefox Browser"*)
            log_warn "  Branding reference in patches: $line"
            branding_issues=true
            ;;
    esac
done < <(grep -roh '^+.*Mozilla Firefox\|^+.*Firefox Browser' "$STGR_PATCHES_DIR" 2>/dev/null || true)

if [ "$branding_issues" = false ]; then
    log_pass "  No leftover Mozilla branding in STGR-added lines"
fi

# Check for about:firefox references
FF_ABOUT=$(grep -rl 'about:firefox' "$STGR_PATCHES_DIR" 2>/dev/null || true)
if [ -n "$FF_ABOUT" ]; then
    log_warn "  'about:firefox' still referenced in: $FF_ABOUT"
    WARNINGS=$((WARNINGS + 1))
else
    log_pass "  No about:firefox references remain"
fi
echo ""

# Check 5: Patch file sizes
CHECKS=$((CHECKS + 1))
log_info "Check 5: Patch file sizes..."
empty_patch=false
for f in "$STGR_PATCHES_DIR"/*.patch; do
    size=$(wc -c < "$f")
    if [ "$size" -lt 50 ]; then
        log_fail "  Empty/minimal patch: $(basename "$f") ($size bytes)"
        empty_patch=true
        ERRORS=$((ERRORS + 1))
    fi
done
if [ "$empty_patch" = false ]; then
    log_pass "  All patches non-empty"
fi
echo ""

# Check 6: Patch git headers
CHECKS=$((CHECKS + 1))
log_info "Check 6: Patch git headers..."
header_issues=false
for f in "$STGR_PATCHES_DIR"/*.patch; do
    name=$(basename "$f")
    if ! head -1 "$f" | grep -q "^From:" 2>/dev/null; then
        log_warn "  Missing 'From:' header: $name"
        header_issues=true
    fi
done
if [ "$header_issues" = false ]; then
    log_pass "  All patches have valid From headers"
else
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "=============================================="
echo " Lint Results: $CHECKS checks, $ERRORS errors, $WARNINGS warnings"
echo "=============================================="

if [ $ERRORS -gt 0 ]; then
    log_fail "Linting found errors that must be fixed."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    log_warn "Linting passed with warnings."
    exit 0
else
    log_pass "All lint checks passed!"
    exit 0
fi
