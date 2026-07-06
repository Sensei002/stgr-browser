# STGR Browser Branding Guide

## Brand Identity

### Name
- **Full name**: STGR Browser
- **Short name**: STGR
- **Always capitalize**: STGR (not Stgr, stgr, or S.T.G.R.)

### Logo
The STGR logo is a `logo.png` located in `branding/`:
- **Dark red accent** (#C41E3A) — the primary brand color
- **Black backdrop** — the foundation of the dark theme
- **Minimalist design** — clean, focused, performance-oriented

### Color Palette

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary | Cardinal Red | `#C41E3A` | Accents, links, highlights, active tab line |
| Secondary | Dark Red | `#8B0000` | Gradients, hover states, depth |
| Accent | Bright Red | `#FF4444` | Glow effects, attention icons, active states |
| Background | Near Black | `#0A0A0A` | Default background (dark) |
| Surface | Dark Charcoal | `#141414` | Cards, panels, toolbars |
| Surface Alt | Charcoal | `#1E1E1E` | Hover states, form fields |
| Text Primary | Light Gray | `#E8E8E8` | Primary text |
| Text Secondary | Muted Gray | `#909090` | Secondary text |
| Success | Green | `#00E676` | Success states |
| Warning | Amber | `#FFC107` | Warning states |
| Error | Red | `#FF5252` | Error states |

### Typography
- **System UI font stack** for maximum performance
- No custom font loading
- `system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`

## Theme Files

### Firefox Theme (WebExtension)
The browser theme is defined in `branding/theme.json`. This is a standard Firefox WebExtension theme applied at build time.

### Key Theme Properties
- **Dark mode by default** — near-black (#0A0A0A) background
- **Red accent** (#C41E3A) for tab line, loading indicators, focus borders
- **Red glow** (#FF4444) for attention icons
- **Compact spacing** for minimal UI

## Logo & Icon Setup

### File Locations

| File | Description |
|------|-------------|
| `branding/logo.png` | **Primary logo** — your custom PNG file |
| `branding/logo.svg` | SVG version with red gradient (fallback/generation source) |
| `branding/icon.png` | Simplified square icon (optional) |
| `branding/icon.svg` | SVG icon with red gradient |

### Required Icon Sizes

| Size | Format | Usage |
|------|--------|-------|
| 16×16 | PNG/ICO | Taskbar, tabs |
| 24×24 | PNG | Context menus |
| 32×32 | PNG/ICO | Alt+Tab, taskbar |
| 48×48 | PNG/ICO | Installer |
| 64×64 | PNG | Start menu |
| 96×96 | PNG | HiDPI displays |
| 128×128 | PNG | Extensions store |
| 256×256 | PNG/ICO | High-res displays |
| 512×512 | PNG/ICNS | App stores, About page |

### Icon Files
- `branding/logo.png` — Your custom logo
- `branding/logo.svg` — SVG source with red gradient
- `branding/icon.svg` — Simplified app icon SVG
- `branding/stgr.ico` — Windows icon (generated)
- `branding/stgr.icns` — macOS icon (generated)

## Rebranding Firefox to STGR

### Files to Replace
The following Firefox branding files need to be replaced in the source:
```
browser/branding/ → stgr/branding/

Firefox-specific strings:
- about:firefox → about:stgr
- Firefox → STGR Browser (in all UI strings)
- Mozilla → STGR (in vendor strings)
- https://www.mozilla.org → https://stgr-browser.dev
```

### Branding Override (via mozconfig)
```bash
ac_add_options --with-app-name=stgr-browser
ac_add_options --with-app-basename=STGR
ac_add_options --with-branding=stgr/branding
```

## Asset Generation

Use `scripts/generate-icons.sh` to generate all icon formats from SVG sources:
```bash
# Generate all icons
./scripts/generate-icons.sh all

# Generate specific formats
./scripts/generate-icons.sh ico    # Windows icons
./scripts/generate-icons.sh icns   # macOS icons
./scripts/generate-icons.sh linux  # Linux icons
```

**Prerequisites**: Inkscape, ImageMagick, iconutil (macOS)

## Theme Customization

### For Users
Users can customize the theme via:
1. **Extensions**: Install any Firefox-compatible theme
2. **Built-in settings**: Dark/Light/Auto mode
3. **about:config**: Advanced color customization

### For Developers
Create custom themes by modifying `branding/theme.json`:
```json
{
  "theme": {
    "colors": {
      "frame": "#YOUR_COLOR",
      "toolbar": "#YOUR_COLOR",
      "tab_line": "#YOUR_ACCENT"
    }
  }
}
```

---

*STGR branding is dark red with black accent — built for gaming, performance, and privacy.*
