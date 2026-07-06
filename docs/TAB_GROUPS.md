# STGR Browser Tab Groups

## Overview

Tab Groups let you organize related tabs together with named, color-coded groups. Groups are displayed in the vertical sidebar with collapsible headers and nested tabs.

## Features

| Feature | Description |
|---------|-------------|
| **Create Group** | From context menu: "New Group with Tab" |
| **Rename Group** | Double-click the group header to rename |
| **Color Labels** | 8 preset colors via context menu |
| **Expand/Collapse** | Click group header to toggle |
| **Drag into Group** | Drag a tab onto a group header to add it |
| **Remove from Group** | Context menu: "Remove from Group" |
| **Delete Group** | Close button on header or context menu |
| **Tab Count Badge** | Shows number of tabs in each group |
| **Visual Nesting** | Grouped tabs are indented 18px in the sidebar |
| **Collapse All** | Ctrl+Shift+G to collapse all groups |
| **Session Persistence** | Groups and membership survive restarts |
| **Ungroup All** | Context menu option on group header |

### Color Palette

| Color | Hex | Preview |
|-------|-----|---------|
| Red | `#C41E3A` | (STGR accent) |
| Green | `#00E676` | |
| Orange | `#FF9100` | |
| Purple | `#B388FF` | |
| Pink | `#FF80AB` | |
| Red | `#FF5252` | |
| Yellow | `#FFD600` | |
| Teal | `#1DE9B6` | |

## Usage

### Creating a Group

1. **Right-click** any tab in the vertical sidebar
2. Select **"New Group with Tab"**
3. Enter a name for the group
4. The tab is now grouped, and more tabs can be added

### Adding Tabs to a Group

| Method | Steps |
|--------|-------|
| **Drag & Drop** | Drag a tab onto the group's header in the sidebar |
| **Context Menu** | Right-click tab → "Add to Group" → select group |

### Managing Groups

| Action | How |
|--------|-----|
| **Expand/Collapse** | Click the group header |
| **Rename** | Double-click the group header |
| **Change Color** | Right-click header → select a color |
| **Close Group** | Click the × button on the header |
| **Select All Tabs** | Right-click header → "Select All in Group" |
| **Ungroup All** | Right-click header → "Ungroup All" |
| **Delete Group** | Right-click header → "Delete Group" |

### Keyboard Shortcut

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+G` | Collapse all groups |

## Architecture

### Data Model

```
TabGroupsManager (singleton)
├── _groups: Map<groupId, GroupData>
│   ├── id: string (auto-increment)
│   ├── name: string
│   ├── color: hex string
│   ├── collapsed: boolean
│   ├── order: number (display order)
│   └── tabIds: Set<string> (persisted tab identifiers)
├── _tabGroup: WeakMap<tab, groupId> (runtime membership)
└── Persistence: JSON in stgr.tabGroups.data pref
```

### Tab Identity

Tab-group membership is stored via a custom **`stgrGroupId`** attribute on the `<tab>` element. Firefox's session store automatically serializes custom attributes, so group membership survives restarts.

The `tabIds` set in each group uses `tab.linkedPanel` as the stable identifier, which is the DOM ID of the tab's browser panel.

### Data Flow

```
User Action → Context Menu / Drag-Drop
                    ↓
         TabGroupsManager.addTabToGroup()
                    ↓
         Sets tab.setAttribute("stgrGroupId", id)
         Saves to stgr.tabGroups.data pref
                    ↓
         Emits "tab-added-to-group" event
                    ↓
         VerticalTabsUI._onGroupsChanged()
                    ↓
         _renderAllTabs() (re-renders with group layout)
```

### Session Restore Flow

```
Browser restart
    ↓
VerticalTabsUI.createPanel()
    ↓
TabGroupsManager.load() — reads stgr.tabGroups.data
    ↓
_renderAllTabs()
    ↓
For each tab: checks tab.getAttribute("stgrGroupId")
    ↓
TabGroupsManager.restoreTabGroup(tab) — restores WeakMap membership
```

## Integration

### With Vertical Tabs

Tab Groups require **vertical tabs** to be enabled. They render as collapsible sections between the pinned tabs area and the ungrouped tabs.

### With Existing Features

- **Pinned tabs**: Always shown above groups, never grouped
- **Tab preview**: Works normally for grouped tabs
- **Drag-drop**: Dragging within a group reorders; dragging to a group header adds to group
- **Search/filter**: Filters tabs within groups too
- **Gaming Mode**: Collapses all groups when activated

## Preferences

| Preference | Default | Description |
|------------|---------|-------------|
| `stgr.tabGroups.enabled` | `true` | Enable tab groups |
| `stgr.tabGroups.showColorDot` | `true` | Show color dot on group headers |
| `stgr.tabGroups.collapseOnStartup` | `false` | Collapse all groups on startup |
| `stgr.tabGroups.data` | `""` | Group definitions (JSON, managed) |

## Development

### Adding New Group Actions

1. Add the action method in `TabGroupsManager.jsm`
2. Add UI integration in `_showGroupContextMenu()` or `_createGroupSection()` in `VerticalTabsUI.jsm`
3. Add CSS styling in `vertical-tabs.css`
4. Add localization strings in `verticaltabs.ftl`

### Testing

```bash
cd gecko-dev
./mach test browser/components/verticaltabs/test
```

### Known Limitations

1. Groups are only visible in vertical tab mode (not in horizontal tab strip)
2. No drag-reorder of entire groups (future enhancement)
3. No nested groups (groups within groups)
4. Color submenu uses simple text labels, not visual color swatches
5. Cannot assign the same tab to multiple groups
