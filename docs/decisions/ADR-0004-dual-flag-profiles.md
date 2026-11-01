# ADR-0004 — Two launch profiles instead of one tuned default

**Status:** accepted
**Date:** 2026-11-01

## Context

The brief asks for the "lowest possible RAM usage". The single most effective Chromium switch
for that is `--process-per-site`: it collapses every tab of the same site into one renderer
process. Combined with `--renderer-process-limit` and disabling the back/forward cache, it
cuts total memory by roughly a third in our measurements.

It also removes per-tab process isolation. With `--process-per-site`, a compromised renderer
covers every tab of that origin rather than one tab. That is a genuine security regression,
not a theoretical one — site isolation is the mitigation Chromium invested most heavily in
over the last decade.

A browser people log into things with cannot make that trade silently.

## Decision

Ship two profiles from one flag source:

- **`balanced`** — the default. Keeps site isolation. Wins memory from aggressive tab
  discarding (`high_efficiency_mode.state = 2`), a renderer cap of 10, and a 256 MB disk
  cache cap.
- **`lowmem`** — opt-in, reachable through a separate Start Menu shortcut
  ("STGR Browser (Low RAM)") that passes `--stgr-lowmem` to the launcher. Adds
  `--process-per-site`, `--renderer-process-limit=4`, `--enable-low-end-device-mode`, a V8
  heap cap, and disables bfcache/prerender.

Both are defined in `config/flags/flags.conf`; `lowmem` is `balanced` plus a computed delta,
so the two can never drift.

## Reasoning

**Consent beats a silent default.** A user on an 8 GB machine can choose the memory profile
that suits them. A user who never thinks about it gets the safe one. Making the aggressive
profile the default would be a decision made on the user's behalf about their own security
posture.

**A visible entry point.** A flag buried in `about:flags` is not a feature. A second
shortcut is discoverable, requires no explanation, and is trivially reversible — close the
window, open the other one.

**One source, two outputs.** Computing `lowmem` as a delta over `balanced` means a change to
the shared base propagates to both, and `--print-flags` makes the difference auditable in
one command.

## Consequences

- Two shortcuts in the Start Menu. Slightly more clutter, considerably more honesty.
- `--process-per-site` in `lowmem` means a crash in one tab takes down every tab of that
  site. Users should be told; the shortcut name plus the docs are the current answer.
- Any future "performance mode" work must decide which profile it belongs to. The rule:
  if it weakens isolation, it goes in `lowmem`; if it only reduces speculative work, it can
  go in `balanced`.
- If benchmarks later show the gap is smaller than 30%, collapse to one profile. Do not keep
  a second profile for its own sake.
