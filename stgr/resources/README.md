# STGR Resources

Shared, static assets used by STGR UI and configuration:

- Brand colors and design tokens live in `stgr/branding/brand.json` (single
  source of truth for visuals).
- Fonts/icons: no external dependencies — the browser uses system fonts and
  the generated logo icon set (`stgr/branding/icons/`).
- Localization: STGR UI strings are English-first; structure the FTL files in
  the Firefox tree so translators can add locales (follow the upstream l10n
  model — see `docs/architecture.md`).

Nothing in this directory may reference a CDN, remote font, or tracking
endpoint — all resources must load offline.
