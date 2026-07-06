# STGR Browser Vertical Tabs

## Overview

Vertical Tabs is an optional layout mode that moves the tab strip from the top of the window to a sidebar on the left side. This provides a more space-efficient way to manage many open tabs, especially on widescreen monitors.

Toggle between horizontal (default) and vertical layout anytime via the toolbar button or keyboard shortcut.

## Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| **Toggle Layout** | Switch between horizontal and vertical tab orientation |
| **Sidebar Panel** | Dedicated left sidebar showing all open tabs |
| **Pinned Tabs Section** | Pinned tabs appear at the top of the sidebar, separated by a divider |
| **Enhanced Tab Search** | Fuzzy search by title + URL, match highlighting, keyboard navigation |
| **Quick Switch** | Ctrl+P anywhere in the sidebar focuses the search box |
| **Drag-and-Drop Reorder** | Reorder tabs by dragging them within the sidebar |
| **Tab Preview on Hover** | Screenshot thumbnail of page content, with title + URL overlay (configurable) |
| **Context Menu** | Full context menu with reload, duplicate, pin, mute, bookmark, copy URL, close |
| **Close Button** | Each tab shows a close button on hover |
| **Mute Button** | Tabs playing audio show a mute button on hover |
| **Loading Indicator** | Spinning indicator for loading tabs |
| **Scrollbar** | Custom thin scrollbar for many tabs |
| **Auto-Hide** | Collapses sidebar to thin strip, expands on hover (VSCode-style) |
| **Keyboard Shortcut** | Ctrl+Shift+E to toggle vertical tabs |
| **Animations** | Smooth transitions and slide-in animations (configurable) |
| **New Tab Button** | Bottom toolbar button to open new tabs |
| **Pin Button** | Pin sidebar open when auto-hide is active |
| **Session Persistence** | Preference is saved across sessions |

### Tab States

The sidebar visually represents all standard tab states:

- **Selected/Active**: Highlighted with accent color and left indicator bar
- **Loading**: Spinning indicator, dimmed label
- **Pinned**: Compact layout, separated section at top
- **Sound Playing**: Audio icon visible on hover
- **Muted**: Muted audio icon
- **Discarded**: Handled gracefully (restores on click)

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+E` | Toggle vertical tabs on/off |
| `Ctrl+Shift+A` | Toggle auto-hide mode (TODO: register in VerticalTabs.jsm) |
| `Ctrl+Shift+G` | Collapse all tab groups |
| `Ctrl+T` | New tab (from bottom bar button) |
| `Escape` | Clear search filter / blur search |
| `Tab` | Navigate between tab items |
| `Enter` | Select focused tab from search results |
| `Ctrl+P` | Focus search box (quick switch) |
| `Up / Down` | Navigate through filtered search results |

## Configuration

### Preferences (about:config)

| Preference | Default | Description |
|------------|---------|-------------|
| `stgr.verticalTabs.enabled` | `false` | Enable vertical tab layout |
| `stgr.verticalTabs.width` | `260` | Sidebar width in pixels |
| `stgr.verticalTabs.animations` | `true` | Enable slide-in animations |
| `stgr.verticalTabs.showPreview` | `true` | Show tab preview on hover |
| `stgr.verticalTabs.showPinnedSection` | `true` | Show separate pinned tabs section |
| `stgr.verticalTabs.autoHide` | `false` | Auto-hide sidebar when not hovering |
| `stgr.verticalTabs.searchEnabled` | `true` | Enable tab search/filter box |
| `stgr.verticalTabs.searchFuzzy` | `true` | Enable fuzzy matching (non-contiguous characters) |
| `stgr.verticalTabs.searchUrls` | `true` | Include page URLs in search |
| `stgr.verticalTabs.previewWidth` | `280` | Tab preview thumbnail width in pixels |
| `stgr.verticalTabs.previewHeight` | `175` | Tab preview thumbnail height in pixels |
| `stgr.verticalTabs.previewQuality` | `70` | JPEG quality for thumbnail (1-100) |

### Via Settings UI

`Settings > General > Layout > Vertical Tabs`

## Architecture

### Component Structure

```
browser/components/verticaltabs/
├── moz.build                    # Build registration
├── VerticalTabs.jsm             # Core singleton: state, prefs, window registry, event bus
├── VerticalTabsUI.jsm           # Per-window UI: DOM creation, rendering, events
├── content/
│   └── vertical-tabs.css        # All visual styling
├── locales/
│   └── en-US/
│       └── verticaltabs.ftl     # Localization strings
```

### Data Flow

```
User Action → gBrowser (Firefox) → Tab Events → VerticalTabs.jsm
                                                          ↓
                                              VerticalTabsUI.jsm
                                                          ↓
                                              DOM Update (sidebar)
```

### Window Lifecycle

1. **Window open**: `browser-window-ready` observer fires → `VerticalTabs._registerWindow()` → creates `VerticalTabsUI` instance
2. **If enabled**: `VerticalTabsUI.createPanel()` → builds sidebar DOM, renders tabs, attaches event listeners
3. **Tab events**: All tab events bubble through `gBrowser.tabContainer` → `VerticalTabs` → `VerticalTabsUI`
4. **Toggle**: `VerticalTabs.toggle()` → updates pref → calls `_onEnabledChanged()` → all windows create/remove panels
5. **Window close**: `unload` event → `VerticalTabsUI.destroy()` → cleanup

## Integration Points

### With Other STGR Features

- **Gaming Mode**: Automatically hides vertical tabs when Gaming Mode activates
- **Tab Groups**: Vertical tabs show group nesting with indentation and visual hierarchy
- **Dark Mode**: Respects system/browser theme settings
- **Compact Mode**: Works with STGR's compact UI density

### With Firefox APIs

| API | Usage |
|-----|-------|
| `gBrowser.tabs` | Tab list access |
| `gBrowser.tabContainer` | Tab event listeners |
| `gBrowser.selectedTab` | Active tab tracking |
| `gBrowser.addTab()` | New tab creation |
| `gBrowser.removeTab()` | Tab closing |
| `gBrowser.moveTabTo()` | Tab reordering |
| `gBrowser.pinTab() / unpinTab()` | Pin state |
| `tab.toggleMuteAudio()` | Audio control |
| `tab.linkedBrowser.currentURI` | URL for preview |
| `Services.prefs` | Preference management |
| `Services.wm.getEnumerator()` | Multi-window support |
| `CustomizableUI.createWidget()` | Toolbar button |
| `PlacesCommandHook.bookmarkLink()` | Bookmark integration |

## Development

### Adding New Tab Features

1. Add event handler in `VerticalTabs.jsm`
2. Add UI method in `VerticalTabsUI.jsm`
3. Add CSS in `vertical-tabs.css`
4. Add localization in `verticaltabs.ftl`

### Testing

```bash
# Unit tests
cd gecko-dev
./mach test browser/components/verticaltabs/test

# Manual testing
./mach run
# Press Ctrl+Shift+E to toggle vertical tabs
```

### Known Limitations

1. **Extension compatibility**: Some tab management extensions may not recognize the vertical layout
2. **Tab strip hiding**: Not all themes handle the tab strip hiding gracefully
3. **Screen reader support**: ARIA attributes are provided but may need refinement
4. **Performance**: Very large numbers of tabs (100+) may cause scroll performance issues
5. **macOS**: Native titlebar integration may require additional tweaks
