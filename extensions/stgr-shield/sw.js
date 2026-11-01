/* STGR Shield - service worker.
 *
 * The blocking itself happens in the network stack via declarativeNetRequest;
 * there is no request interception in JS. This worker only:
 *   1. turns on the per-tab blocked counter badge,
 *   2. keeps the badge readable (counts above 99 are shown as "99+").
 *
 * It must stay idle-friendly: a heavy service worker is the fastest way to
 * lose the memory advantage the compiled ruleset bought us.
 */

const DEFAULTS = { enabled: true };

chrome.runtime.onInstalled.addListener(async () => {
  const stored = await chrome.storage.local.get(DEFAULTS);
  await chrome.storage.local.set(stored);

  // Chromium renders the DNR match count as badge text for us - no polling,
  // no per-request JS. This is the whole reason the badge is cheap.
  await chrome.declarativeNetRequest.setExtensionActionOptions({
    displayActionCountAsBadgeText: stored.enabled !== false
  });
});

chrome.runtime.onStartup.addListener(async () => {
  const { enabled } = await chrome.storage.local.get(DEFAULTS);
  await chrome.declarativeNetRequest.setExtensionActionOptions({
    displayActionCountAsBadgeText: enabled !== false
  });
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== "local" || !changes.enabled) return;
  chrome.declarativeNetRequest.setExtensionActionOptions({
    displayActionCountAsBadgeText: changes.enabled.newValue !== false
  });
});
