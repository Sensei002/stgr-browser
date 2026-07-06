#!/bin/bash
# STGR Browser - Icon Generator Shell Wrapper
# Calls the Python script to generate all icon formats from branding/logo.png
#
# Usage:
#   ./scripts/generate-icons.sh              # Generate all icons
#   ./scripts/generate-icons.sh --logo path  # Use custom logo path

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "=== STGR Browser Icon Generator ==="
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
python scripts/generate-icons.py "$@"

echo ""
echo "=== Done ==="
echo ""
echo "On macOS, generate .icns with:"
echo "  iconutil -c icns branding/icons/stgr.iconset -o branding/stgr.icns"
