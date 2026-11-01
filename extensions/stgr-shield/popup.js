/* STGR Shield - popup controller. */

const toggle = document.getElementById("toggle");
const ruleCount = document.getElementById("rule-count");
const blockedTab = document.getElementById("blocked-tab");
const listState = document.getElementById("list-state");

async function totalRules() {
  const manifest = chrome.runtime.getManifest();
  const resources = (manifest.declarative_net_request?.rule_resources) || [];
  const enabled = resources.filter((r) => r.enabled);
  return enabled.length;
}

async function blockedOnActiveTab() {
  // getMatchedRules is only available for unpacked extensions; degrade quietly.
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return null;
    const res = await chrome.declarativeNetRequest.getMatchedRules({
      tabId: tab.id,
      minTimeStamp: Date.now() - 1000 * 60 * 60 * 24
    });
    return res.rulesMatchedInfo.length;
  } catch (err) {
    return null;
  }
}

async function init() {
  const { enabled } = await chrome.storage.local.get({ enabled: true });
  toggle.checked = enabled !== false;

  const lists = await totalRules();
  ruleCount.textContent = lists > 0
    ? `${lists} ruleset${lists === 1 ? "" : "s"} active`
    : "No ruleset loaded";
  listState.textContent = lists > 0 ? "Compiled" : "Missing";

  const count = await blockedOnActiveTab();
  blockedTab.textContent = count === null ? "n/a" : String(count);
}

toggle.addEventListener("change", async () => {
  const enabled = toggle.checked;
  await chrome.storage.local.set({ enabled });

  const resources = chrome.runtime.getManifest().declarative_net_request?.rule_resources || [];
  for (const resource of resources) {
    try {
      await chrome.declarativeNetRequest.updateEnabledRulesets(
        enabled ? { enableRulesetIds: [resource.id] } : { disableRulesetIds: [resource.id] }
      );
    } catch (err) {
      // Ruleset id may already be in the requested state - harmless.
    }
  }
});

init();
