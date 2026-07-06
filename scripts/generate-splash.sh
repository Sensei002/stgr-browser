#!/bin/bash
# STGR Browser - Splash Screen Generator
# Generates assets/splash-screen.svg with the actual logo.png embedded as base64.
#
# Usage:
#   ./scripts/generate-splash.sh                          # Default
#   ./scripts/generate-splash.sh --logo path/to/logo.png  # Custom logo path

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "=== STGR Browser Splash Screen Generator ==="
echo "Project: $PROJECT_DIR"
echo ""

# Check that logo exists
if [ ! -f "branding/logo.png" ]; then
    echo "ERROR: branding/logo.png not found!"
    echo "Place your logo at branding/logo.png first."
    exit 1
fi

# Check for Pillow
python -c "from PIL import Image; print('Pillow OK')" 2>/dev/null || {
    echo "ERROR: Python Pillow library not found."
    echo "Install it: pip install Pillow"
    exit 1
}

# Run the generator
python scripts/generate-splash.py "$@"

echo ""
echo "=== Done ==="
echo "Splash screen saved to assets/splash-screen.svg"
