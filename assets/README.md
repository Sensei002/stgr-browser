# STGR Browser Assets

This directory contains static assets used by STGR Browser.

## Files

| File | Description |
|------|-------------|
| `splash-screen.svg` | Browser splash screen shown on startup (generated from `branding/logo.png`) |
| `favicon.svg` | (planned) Website favicon for stgr-browser.dev |

## Generating Assets

### Splash Screen

The splash screen is auto-generated from `branding/logo.png`:

```bash
# Generate or update the splash screen with the current logo
./scripts/generate-splash.sh
```

This embeds the actual logo as a base64 PNG inside an SVG template with:
- Dark background with subtle grid overlay
- Red glow behind the logo (#C41E3A accent)
- Animated loading bar
- "STGR BROWSER" title and "STARTING..." subtitle
- Version number from `branding/branding-config.json`

### Icons

SVG source files are located in `branding/`. Use `scripts/generate-icons.sh` to generate raster versions in all required sizes.
