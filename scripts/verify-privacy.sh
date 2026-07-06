#!/bin/bash
# ============================================================================
# STGR Browser - Privacy Verification Script
# ============================================================================
# Verifies that no telemetry, data collection, or tracking code remains
# in the Firefox source after applying STGR patches.
#
# Usage:
#   ./scripts/verify-privacy.sh              # Check gecko-dev source
#   ./scripts/verify-privacy.sh --patches    # Check patches instead
#   ./scripts/verify-privacy.sh --help       # Show this help
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

TOTAL_CHECKS=0
PASSED=0
FAILED=0
WARNINGS=0

# Assert a pattern does NOT appear in the given path
check_no_match() {
    local label="$1"
    local pattern="$2"
    local path="$3"
    local exclude="${4:-}"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    # Build find arguments array
    local -a find_args=(
        "$path" -type f \
        \( -name '*.cpp' -o -name '*.h' -o -name '*.js' -o \
           -name '*.jsm' -o -name '*.json' -o -name '*.toml' -o \
           -name '*.py' -o -name '*.rs' \)
    )

    # Handle comma-separated exclude directories properly
    if [ -n "$exclude" ]; then
        local saved_ifs="$IFS"
        IFS=','
        for dir in $exclude; do
            dir="${dir# }"  # strip leading space
            dir="${dir% }"  # strip trailing space
            [ -n "$dir" ] && find_args+=('!' '-path' "*/$dir/*")
        done
        IFS="$saved_ifs"
    fi

    find_args+=(-exec grep -l "$pattern" {} +)

    local results
    results=$(find "${find_args[@]}" 2>/dev/null || true)

    if [ -z "$results" ]; then
        log_pass "$label — no matches found"
        PASSED=$((PASSED + 1))
    else
        local count
        count=$(echo "$results" | wc -l | tr -d ' ')
        count=${count:-0}
        log_fail "$label — found $count file(s) with matches:"
        echo "$results" | while IFS= read -r line; do
            echo "         $line"
        done
        FAILED=$((FAILED + 1))
    fi
}

# Assert a pattern DOES appear at least min_expected times in the given path
check_contains_all() {
    local label="$1"
    local pattern="$2"
    local path="$3"
    local min_expected="${4:-1}"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    local count
    count=$(grep -rl "$pattern" "$path" 2>/dev/null | wc -l | tr -d ' ')
    count=${count:-0}

    if [ "$count" -ge "$min_expected" ] 2>/dev/null; then
        log_pass "$label — found in $count file(s)"
        PASSED=$((PASSED + 1))
    else
        log_warn "$label — expected in at least $min_expected file(s), found in $count"
        WARNINGS=$((WARNINGS + 1))
    fi
}

echo "=============================================="
echo " STGR Browser - Privacy Verification"
echo "=============================================="
echo ""

if [ "${1:-}" = "--patches" ] || [ ! -d "$STGR_SOURCE_DIR" ]; then
    # ========================================================================
    # PATCHES MODE — Verify that the removal patches include all necessary
    # references. In this mode, we use check_contains_all (not check_no_match)
    # because patches MUST reference the telemetry/Pocket paths they remove.
    # ========================================================================
    log_info "Checking patches directory: $STGR_PATCHES_DIR"
    echo ""
    echo "--- Telemetry Removal Patches ---"

    check_contains_all "Telemetry core removed" "toolkit/components/telemetry" "$STGR_PATCHES_DIR" 1
    check_contains_all "Telemetry prefs disabled" "toolkit.telemetry" "$STGR_PATCHES_DIR" 1
    check_contains_all "Data reporting disabled" "datareporting" "$STGR_PATCHES_DIR" 1
    check_contains_all "Crash reporting disabled" "crashreporter" "$STGR_PATCHES_DIR" 1

    echo ""
    echo "--- Pocket Removal Patches ---"

    check_contains_all "Pocket extension removed" "extensions.pocket" "$STGR_PATCHES_DIR" 1

    echo ""
    echo "--- Sponsored Content Removal Patches ---"

    check_contains_all "Sponsored suggestions removed" "browser.urlbar.quicksuggest" "$STGR_PATCHES_DIR" 1
    check_contains_all "Shopping component removed" "browser.shopping" "$STGR_PATCHES_DIR" 1

    echo ""
    echo "--- Sync/Account Removal Patches ---"

    check_contains_all "Firefox Sync removed" "services.sync" "$STGR_PATCHES_DIR" 1
    check_contains_all "Firefox Accounts removed" "fxaccounts" "$STGR_PATCHES_DIR" 1

    echo ""
    echo "--- Experiment/Study Removal Patches ---"

    check_contains_all "Normandy removed" "normandy" "$STGR_PATCHES_DIR" 1

    echo ""
    echo "--- Privacy-Enhancing Patches ---"

    check_contains_all "HTTPS-Only mode enabled" "dom.security.https_only_mode" "$STGR_PATCHES_DIR" 1
    check_contains_all "Tracking protection enabled" "privacy.trackingprotection" "$STGR_PATCHES_DIR" 1
    check_contains_all "DNS-over-HTTPS configured" "network.trr" "$STGR_PATCHES_DIR" 1
    check_contains_all "Fingerprinting protection" "resistFingerprinting" "$STGR_PATCHES_DIR" 1

else
    # ========================================================================
    # SOURCE MODE — Verify the built/cloned Firefox source has no remaining
    # telemetry, Pocket, or tracking code.
    # ========================================================================
    log_info "Checking Firefox source: $STGR_SOURCE_DIR"
    echo ""
    echo "--- Telemetry Checks ---"

    check_no_match "Telemetry core toolkit" "toolkit/components/telemetry" "$STGR_SOURCE_DIR" "third_party"
    check_no_match "Telemetry server URLs" "telemetry\.mozilla\.org" "$STGR_SOURCE_DIR" "third_party"
    check_no_match "Telemetry preferences" "toolkit\.telemetry\.enabled" "$STGR_SOURCE_DIR" "test,third_party"
    check_no_match "Studies (Normandy)" "toolkit/components/normandy" "$STGR_SOURCE_DIR" "third_party"

    echo ""
    echo "--- Pocket Checks ---"

    check_no_match "Pocket extension code" "browser/components/pocket" "$STGR_SOURCE_DIR" ""
    check_no_match "Pocket preferences" "extensions\.pocket\." "$STGR_SOURCE_DIR" "test,third_party"

    echo ""
    echo "--- Sync & Account Checks ---"

    check_no_match "Sync service code" "services/sync" "$STGR_SOURCE_DIR" "third_party"
    check_no_match "Firefox Accounts code" "services/fxaccounts" "$STGR_SOURCE_DIR" "third_party"

    echo ""
    echo "--- Sponsored Content Checks ---"

    check_no_match "Shopping component" "browser/components/shopping" "$STGR_SOURCE_DIR" ""
    check_no_match "Sponsored top sites code" "showSponsored" "$STGR_SOURCE_DIR" "test,third_party"

    echo ""
    echo "--- STGR-Specific Checks ---"

    check_contains_all "STGR preferences applied" "stgr\." "$STGR_SOURCE_DIR/stgr" 1 || true
    check_contains_all "STGR branding present" "STGR Browser" "$STGR_SOURCE_DIR/stgr/branding" 1 || true
    check_contains_all "STGR mozconfig present" "stgr/branding" "$STGR_SOURCE_DIR/mozconfig" 1 || true
fi

echo ""
echo "=============================================="
echo " Results: $PASSED/$TOTAL_CHECKS passed, $FAILED failed, $WARNINGS warnings"
echo "=============================================="

if [ "$FAILED" -gt 0 ]; then
    echo ""
    log_fail "Privacy verification found issues that need attention."
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo ""
    log_warn "Privacy verification passed with warnings."
    exit 0
else
    echo ""
    log_pass "All privacy checks passed!"
    exit 0
fi
