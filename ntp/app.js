/* ============================================================================
   STGR Browser - New Tab Page behaviour
   No network calls. No telemetry. Everything renders from STGR_CONFIG, which
   is generated from branding/brand.json at build time.
   ========================================================================== */

(function () {
  "use strict";

  var cfg = window.STGR_CONFIG || {};
  var MAX_TILES = 6;

  /* ── inline icon set (no external requests, no icon-font download) ─────── */

  var ICONS = {
    youtube:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="5.5" width="20" height="13" rx="4" fill="#FF0033"/><path d="M10 9.2v5.6l5-2.8z" fill="#fff"/></svg>',
    github:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#F2F2F4" d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.1-1.47-1.1-1.47-.9-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.88 1.52 2.32 1.08 2.88.82.09-.64.35-1.08.63-1.33-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02a9.4 9.4 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 0 0 0 12 2z"/></svg>',
    discord:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#5865F2" d="M19.3 5.4A16.2 16.2 0 0 0 15.3 4l-.3.6a12 12 0 0 0-6 0L8.7 4a16.2 16.2 0 0 0-4 1.4C2.2 9.2 1.6 12.9 2 16.5a16.5 16.5 0 0 0 5 2.5l.6-1a10.7 10.7 0 0 1-1.7-.8l.4-.3a11.6 11.6 0 0 0 11.4 0l.4.3c-.5.3-1.1.6-1.7.8l.6 1a16.5 16.5 0 0 0 5-2.5c.5-4.2-.6-7.8-2.7-11.1zM8.9 14.3c-1 0-1.8-.9-1.8-2s.8-2 1.8-2 1.8.9 1.8 2-.8 2-1.8 2zm6.2 0c-1 0-1.8-.9-1.8-2s.8-2 1.8-2 1.8.9 1.8 2-.8 2-1.8 2z"/></svg>',
    twitch:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#9146FF" d="M4 3h16v11l-4 4h-3l-3 3H8v-3H4z"/><path fill="#fff" d="M9 7h2v5H9zm5 0h2v5h-2z"/></svg>',
    stgr:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#E01A24" d="M12 2 3 6v6c0 5 4 8.6 9 10 5-1.4 9-5 9-10V6z"/><path fill="#08080A" d="m7.6 10.2 1.5-1.4c.7.6 1.5 1 2.4 1 .9 0 1.4-.3 1.4-.9 0-.5-.3-.8-1.4-1.1l-1.2-.3c-1.6-.4-2.6-1.2-2.6-2.8 0-1.8 1.5-3 3.7-3 1.5 0 2.7.5 3.6 1.3l-1.4 1.5c-.6-.5-1.3-.9-2.2-.9-.8 0-1.3.3-1.3.8 0 .5.4.7 1.4 1l1.2.3c1.8.5 2.7 1.4 2.7 2.9 0 2-1.6 3.1-3.9 3.1-1.6 0-3-.6-3.9-1.5z"/></svg>',
    generic:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="#9A9AA6" stroke-width="1.6"/><path d="M3.2 12h17.6M12 3.2c2.6 2.6 2.6 15 0 17.6M12 3.2c-2.6 2.6-2.6 15 0 17.6" fill="none" stroke="#9A9AA6" stroke-width="1.4"/></svg>',
    add:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>'
  };

  /* ── brand tokens ─────────────────────────────────────────────────────── */

  function applyBrand() {
    var c = cfg.colors || {};
    var root = document.documentElement.style;
    var map = {
      "--red": c.red,
      "--red-bright": c.redBright,
      "--red-deep": c.redDeep,
      "--gold": c.gold,
      "--black": c.black,
      "--surface": c.surface,
      "--surface-alt": c.surfaceAlt,
      "--border": c.border,
      "--text": c.text,
      "--muted": c.muted
    };
    Object.keys(map).forEach(function (key) {
      if (map[key]) root.setProperty(key, map[key]);
    });
  }

  /* ── search ───────────────────────────────────────────────────────────── */

  function looksLikeUrl(value) {
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(value)) return true;
    if (/^localhost(:\d+)?(\/|$)/i.test(value)) return true;
    if (/^\d{1,3}(\.\d{1,3}){3}(:\d+)?(\/|$)/.test(value)) return true;
    // bare domain with a known-ish TLD
    return /^[^\s/]+\.[a-z]{2,}(:\d+)?(\/.*)?$/i.test(value) && !/\s/.test(value);
  }

  function normaliseUrl(value) {
    var v = value.trim();
    if (!v) return null;
    if (looksLikeUrl(v)) return /^[a-z][a-z0-9+.-]*:\/\//i.test(v) ? v : "https://" + v;
    var engine = (cfg.search && cfg.search.url) || "https://duckduckgo.com/?q={query}";
    return engine.replace("{query}", encodeURIComponent(v));
  }

  function navigate(url) {
    if (!url) return;
    window.location.href = url;
  }

  function wireSearch() {
    var form = document.getElementById("search-form");
    var input = document.getElementById("search-input");
    if (!form || !input) return;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var target = normaliseUrl(input.value);
      if (target) navigate(target);
    });

    input.addEventListener("keydown", function (event) {
      if (event.key === "Escape") input.value = "";
    });
  }

  /* ── speed dial ───────────────────────────────────────────────────────── */

  function makeTile(item) {
    var a = document.createElement("a");
    a.className = "tile";
    a.href = item.url;
    a.title = item.url;
    a.setAttribute("data-label", item.label);

    var glyph = document.createElement("span");
    glyph.className = "glyph";
    glyph.innerHTML = ICONS[item.icon] || ICONS.generic;

    var label = document.createElement("span");
    label.className = "label";
    label.textContent = item.label;

    a.appendChild(glyph);
    a.appendChild(label);

    if (item.custom) {
      a.addEventListener("contextmenu", function (event) {
        event.preventDefault();
        removeCustomTile(item.url);
      });
    }
    return a;
  }

  function makeAddTile() {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tile is-add";
    btn.innerHTML =
      '<span class="glyph">' + ICONS.add + "</span>" +
      '<span class="label">Add Site</span>';
    btn.addEventListener("click", addCustomTile);
    return btn;
  }

  function renderDial(custom) {
    var dial = document.getElementById("dial");
    if (!dial) return;
    dial.textContent = "";

    var base = (cfg.speedDial || []).slice();
    var all = base.concat(custom || []).slice(0, MAX_TILES - 1);
    all.forEach(function (item) {
      dial.appendChild(makeTile(item));
    });
    dial.appendChild(makeAddTile());
  }

  function store() {
    return (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local)
      ? chrome.storage.local
      : null;
  }

  function loadCustomTiles(done) {
    var s = store();
    if (!s) return done([]);
    s.get({ stgrTiles: [] }, function (data) {
      done(Array.isArray(data.stgrTiles) ? data.stgrTiles : []);
    });
  }

  function saveCustomTiles(list) {
    var s = store();
    if (!s) return;
    s.set({ stgrTiles: list });
  }

  function addCustomTile() {
    var raw = window.prompt("Site address (example.com)");
    if (!raw) return;
    var url = normaliseUrl(raw);
    if (!url) return;

    var host;
    try {
      host = new URL(url).hostname.replace(/^www\./, "");
    } catch (err) {
      return;
    }

    loadCustomTiles(function (list) {
      list.push({ label: host, url: url, icon: "generic", custom: true });
      saveCustomTiles(list);
      renderDial(list);
    });
  }

  function removeCustomTile(url) {
    loadCustomTiles(function (list) {
      var next = list.filter(function (item) { return item.url !== url; });
      saveCustomTiles(next);
      renderDial(next);
    });
  }

  /* ── version label ────────────────────────────────────────────────────── */

  function stampVersion() {
    var el = document.getElementById("status-version");
    if (el && cfg.version) el.textContent = cfg.name + " v" + cfg.version;
  }

  /* ── boot ─────────────────────────────────────────────────────────────── */

  applyBrand();
  stampVersion();
  wireSearch();
  loadCustomTiles(renderDial);

  var input = document.getElementById("search-input");
  if (input) {
    window.requestAnimationFrame(function () { input.focus(); });
  }
})();
