# STGR Browser Preferences Pane Integration

This guide explains how to integrate the STGR preferences pane into Firefox's `about:preferences`.

## Files in this Patch

| File | Description | Status |
|------|-------------|--------|
| `patches/0015-stgr-preferences-pane.patch` | Creates `stgr.js`, `stgr.ftl`, updates `moz.build` and `VerticalTabsUI.jsm` | Auto-applied |
| `browser/components/preferences/in-content/stgr.js` | Pane controller with pref bindings and lifecycle | Created |
| `browser/locales/en-US/browser/preferences/stgr.ftl` | Localization strings | Created |

## Manual Integration Steps

The following files need manual edits after cloning the Firefox source:

### 1. Add category entry to `browser/components/preferences/in-content/preferences.xhtml`

Find the category list sidebar (search for `category-privacy` or similar) and add:

```xml
<!-- STGR Browser -->
<vbox id="category-stgr" class="category"
      data-category="paneSTGR"
      data-l10n-id="category-stgr">
</vbox>
```

Then find the pane templates section and add before the closing `</html:template>`:

```xml
<!-- STGR Browser -->
<html:template id="paneSTGR" xmlns="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"
               xmlns:html="http://www.w3.org/1999/xhtml">
  <html:h1 data-l10n-id="stgr-pane-header"/>

  <groupbox id="stgrVerticalTabsGroup">
    <caption><label data-l10n-id="stgr-vertical-tabs-header"/></caption>
    <vbox>
      <checkbox id="stgrVerticalTabsEnabled"
                data-l10n-id="stgr-vertical-tabs-enabled"/>
      <hbox align="center">
        <label data-l10n-id="stgr-vertical-tabs-width"
               control="stgrVerticalTabsWidth" flex="1"/>
        <html:input type="range" id="stgrVerticalTabsWidth"
                    min="200" max="400" step="10"/>
        <label id="stgrVerticalTabsWidthValue"/>
      </hbox>
      <checkbox id="stgrVerticalTabsAutoHide"
                data-l10n-id="stgr-vertical-tabs-auto-hide"/>
      <checkbox id="stgrVerticalTabsShowPreview"
                data-l10n-id="stgr-vertical-tabs-show-preview"/>
      <checkbox id="stgrVerticalTabsSearchEnabled"
                data-l10n-id="stgr-vertical-tabs-search-enabled"/>
      <checkbox id="stgrVerticalTabsSearchFuzzy"
                data-l10n-id="stgr-vertical-tabs-search-fuzzy"/>
      <checkbox id="stgrVerticalTabsSearchUrls"
                data-l10n-id="stgr-vertical-tabs-search-urls"/>
      <checkbox id="stgrVerticalTabsAnimations"
                data-l10n-id="stgr-vertical-tabs-animations"/>
    </vbox>
  </groupbox>

  <groupbox id="stgrTabGroupsGroup">
    <caption><label data-l10n-id="stgr-tab-groups-header"/></caption>
    <vbox>
      <checkbox id="stgrTabGroupsEnabled"
                data-l10n-id="stgr-tab-groups-enabled"/>
      <checkbox id="stgrTabGroupsShowColorDot"
                data-l10n-id="stgr-tab-groups-show-color-dot"/>
      <checkbox id="stgrTabGroupsCollapseOnStartup"
                data-l10n-id="stgr-tab-groups-collapse-on-startup"/>
    </vbox>
  </groupbox>

  <groupbox id="stgrPreviewGroup">
    <caption><label data-l10n-id="stgr-tab-preview-header"/></caption>
    <vbox>
      <hbox align="center">
        <label data-l10n-id="stgr-tab-preview-width"
               control="stgrPreviewWidth" flex="1"/>
        <html:input type="range" id="stgrPreviewWidth"
                    min="200" max="500" step="10"/>
        <label id="stgrPreviewWidthValue"/>
      </hbox>
      <hbox align="center">
        <label data-l10n-id="stgr-tab-preview-height"
               control="stgrPreviewHeight" flex="1"/>
        <html:input type="range" id="stgrPreviewHeight"
                    min="100" max="400" step="10"/>
        <label id="stgrPreviewHeightValue"/>
      </hbox>
      <hbox align="center">
        <label data-l10n-id="stgr-tab-preview-quality"
               control="stgrPreviewQuality" flex="1"/>
        <html:input type="range" id="stgrPreviewQuality"
                    min="10" max="100" step="5"/>
        <label id="stgrPreviewQualityValue"/>
      </hbox>
    </vbox>
  </groupbox>

  <groupbox id="stgrGamingModeGroup">
    <caption><label data-l10n-id="stgr-gaming-mode-header"/></caption>
    <vbox>
      <checkbox id="stgrGamingModeEnabled"
                data-l10n-id="stgr-gaming-mode-enabled"/>
    </vbox>
  </groupbox>

  <groupbox id="stgrAboutGroup">
    <caption><label data-l10n-id="stgr-about-header"/></caption>
    <vbox>
      <hbox align="center">
        <label data-l10n-id="stgr-about-version"/>
        <label id="stgrAboutVersion"/>
      </hbox>
      <hbox align="center">
        <label data-l10n-id="stgr-about-build"/>
        <label id="stgrAboutBuild"/>
      </hbox>
      <hbox align="center">
        <label data-l10n-id="stgr-about-platform"/>
        <label id="stgrAboutPlatform"/>
      </hbox>
    </vbox>
  </groupbox>

  <script src="chrome://browser/content/preferences/in-content/stgr.js"/>
</html:template>
```

Also add the FTL localization link in the `<head>` section:

```xml
<html:link rel="localization" href="browser/preferences/stgr.ftl"/>
```

### 2. Add pane loading to `browser/components/preferences/in-content/preferences.js`

Find the pane initialization switch statement and add:

```js
case "paneSTGR":
  STGRPreferences.init();
  break;
```

Find the pane cleanup section and add:

```js
STGRPreferences.shutdown();
```

### 3. Verify build registration

The `0015-stgr-preferences-pane.patch` already updates `moz.build` to include:

```python
FINAL_TARGET_SCRIPTS += [
    "stgr.js",
]
```

## Verification

After building, navigate to `about:preferences#stgr` or click the STGR category in the sidebar. The pane should show all five sections:

1. **Vertical Tabs** — toggle, width slider, auto-hide, preview, search options
2. **Tab Groups** — toggle, color dot, collapse on startup
3. **Tab Preview** — width, height, quality sliders
4. **Gaming Mode** — enable toggle
5. **About** — version, build ID, platform
