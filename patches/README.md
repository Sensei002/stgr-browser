# STGR Browser Patches

This directory contains optimization and customization patches for the Firefox source code.

## Patch Order

Patches should be applied in numerical order. Each patch builds on the previous ones.

| #  | Patch | Category | Description |
|----|-------|----------|-------------|
| 01 | remove-telemetry | Privacy | Removes all Mozilla telemetry, studies, experiments, and data collection |
| 02 | remove-pocket-sync | Privacy | Removes Pocket integration and Firefox Sync |
| 03 | remove-sponsored-content | Privacy | Removes sponsored content, recommendations, and shopping features |
| 04 | memory-optimizations | Performance | Aggressive memory management and cache optimization |
| 05 | gpu-optimizations | Performance | WebRender, GPU scheduling, and hardware acceleration optimization |
| 06 | gaming-mode | Feature | Gaming mode detection and automatic performance tuning |
| 07 | ui-customization | UI | STGR Browser UI, branding, and theme changes |
| 08 | privacy-defaults | Privacy | Default privacy-enhancing configuration |
| 09 | startup-optimizations | Performance | Startup time and initialization optimization |
| 10 | vertical-tabs | Feature | Optional vertical tab sidebar with drag-drop, preview, search, pinned tabs |
| 11 | tab-groups | Feature | Tab groups with color labels, drag-drop into groups, expand/collapse, visual nesting |
| 12 | tab-preview-screenshots | Enhancement | Screenshot thumbnails for tab preview using PageThumbs/drawWindow |
| 13 | auto-hide | Feature | VSCode-style auto-hide sidebar — collapses to thin strip, expands on hover |
| 14 | enhanced-tab-search | Enhancement | Fuzzy title+URL search, match highlighting, keyboard nav, Ctrl+P quick switch |
| 15 | stgr-preferences-pane | Feature | `about:preferences#stgr` pane with Vertical Tabs, Tab Groups, Tab Preview, Gaming Mode, About sections |

## Patch Format

Each patch is a standard unified diff format that can be applied with:

```bash
git apply patches/0001-remove-telemetry.patch
```

Or via the included script:

```bash
./scripts/apply-patches.sh
```

## Manual Patch Application

If patches fail to apply cleanly due to Firefox source changes, you may need to:

1. Apply with `--reject` to see conflict locations:
   ```bash
   git apply --reject patches/XXXX-name.patch
   ```
2. Fix conflicts in the `.rej` files
3. Remove `.rej` files after resolution
4. Commit changes

## Files To Modify Directly

Some changes cannot be expressed as clean patches and require manual file modifications:

### Branding Files (in `stgr/branding/`)
- `configure.sh` - Update `MOZ_APP_NAME`, `MOZ_APP_BASENAME`, `MOZ_APP_VENDOR`
- `branding.nsi` - NSIS installer branding (Windows)
- `firefox-branding.js` - Browser branding strings

### Source Files to Rename
- `browser/branding/` → `stgr/branding/`
- `browser/locales/en-US/browser/branding/` → STGR branding strings
- Replace all "Firefox" strings in UI with "STGR Browser"
- Replace all "Mozilla" strings with "STGR"

### Build Configuration
- `mozconfig` - Already provided in `config/mozconfig`

## Verifying Patches

After applying patches, verify:

1. No telemetry URLs remain:
   ```bash
   grep -r "telemetry" --include="*.cpp" --include="*.h" --include="*.js" --include="*.json" | grep -v "test" | grep -v "third_party"
   ```

2. No Pocket references remain:
   ```bash
   grep -ri "pocket" --include="*.cpp" --include="*.h" --include="*.js" | grep -v "test" | grep -v "third_party"
   ```

3. Build configuration is correct:
   ```bash
   cd gecko-dev && ./mach configure
   ```

## Creating New Patches

To create a new patch after modifying source files:

```bash
cd gecko-dev
git diff > ../patches/XXXX-description.patch
```
