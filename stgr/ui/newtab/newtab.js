/* STGR Browser — New Tab logic.
 * Deliberately dependency-free. No network calls, no analytics, no cookies.
 * Shortcuts are stored in localStorage only (per profile, offline).
 */
"use strict";

const SHORTCUTS_KEY = "stgr.newtab.shortcuts.v1";

function pad(n) { return String(n).padStart(2, "0"); }

function updateClock() {
  const now = new Date();
  const clock = document.getElementById("clock");
  const date = document.getElementById("date");
  if (clock) clock.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
  if (date) {
    date.textContent = now.toLocaleDateString(undefined, {
      weekday: "long", year: "numeric", month: "long", day: "numeric",
    });
  }
}

function tileIcon(name) {
  return (name.trim()[0] || "?").toUpperCase();
}

function renderShortcuts() {
  const host = document.getElementById("shortcuts");
  if (!host) return;
  host.textContent = "";
  let tiles = [];
  try { tiles = JSON.parse(localStorage.getItem(SHORTCUTS_KEY) || "[]"); }
  catch { tiles = []; }

  tiles.forEach((tile, index) => {
    const a = document.createElement("a");
    a.className = "tile";
    a.href = tile.url;
    a.title = tile.url;
    a.innerHTML =
      `<span class="icon">${tileIcon(tile.name)}</span>` +
      `<span class="label"></span>`;
    a.querySelector(".label").textContent = tile.name;

    const remove = document.createElement("span");
    remove.className = "remove";
    remove.textContent = "✕";
    remove.addEventListener("click", (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      tiles.splice(index, 1);
      localStorage.setItem(SHORTCUTS_KEY, JSON.stringify(tiles));
      renderShortcuts();
    });
    a.prepend(remove);
    host.appendChild(a);
  });

  const add = document.createElement("button");
  add.className = "tile add";
  add.type = "button";
  add.innerHTML = `<span class="icon" style="background:none;color:#666">+</span><span class="label">Add</span>`;
  add.addEventListener("click", () => {
    const name = prompt("Shortcut name");
    if (!name) return;
    let url = prompt("URL (https://…)");
    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = "https://" + url;
    tiles.push({ name: name.slice(0, 24), url });
    localStorage.setItem(SHORTCUTS_KEY, JSON.stringify(tiles));
    renderShortcuts();
  });
  host.appendChild(add);
}

document.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 15_000);
  renderShortcuts();
  const input = document.getElementById("search-input");
  if (input) input.focus();
});
