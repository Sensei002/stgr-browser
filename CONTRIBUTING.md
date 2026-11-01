# Contributing

This project is built and maintained primarily by AI agents, with human review. The
contribution rules are therefore optimised for machine-checkable correctness rather than
social convention.

**Read [AGENTS.md](AGENTS.md) first.** It contains the invariants. This file only covers the
mechanics.

---

## Before you open a PR

Run the same checks CI runs:

```bash
python -m compileall -q scripts branding
python scripts/check-brand.py
python scripts/gen-ntp-config.py
python scripts/build-shield-rules.py --offline
node --check ntp/app.js
python scripts/build.py --print-flags balanced
```

All must pass. A PR that fails `validate` will not be reviewed.

---

## What makes a good change

- **One concern per commit.** "Fix NTP spacing and bump the engine" is two commits.
- **Regenerate derived files.** If you change `brand.json` or `VERSION`, commit the
  regenerated `ntp/config.js` and `ntp/manifest.json` in the same commit. CI does not
  auto-commit.
- **Explain the mechanism, not the intention.** In a flag comment, "stops the component
  updater from polling" beats "improves performance".
- **Update the doc that owns the topic.** Flags → `docs/PERFORMANCE.md`. Network behaviour →
  `docs/PRIVACY.md`. Architecture → `docs/ARCHITECTURE.md`.
- **Write an ADR** if someone might reasonably reverse your decision in six months.

---

## What will be rejected

- A new product string hardcoded outside `branding/brand.json`.
- A hand-edit to a file marked auto-generated.
- A new network call without a `docs/PRIVACY.md` update.
- A switch that increases idle CPU or battery drain (see the banned list in
  `docs/PERFORMANCE.md`).
- Moving `--process-per-site` into the `balanced` profile.
- Any change that makes the browser require administrator rights.

---

## Adding a blocked domain

Edit `config/blocklists/stgr-core.txt`, then:

```bash
python scripts/build-shield-rules.py --offline
```

Rules of thumb:

- Only add a domain that serves advertising or tracking, never one that also serves content.
- Prefer the registrable domain (`example.com`) over deep subdomains; the `||domain^` filter
  already matches subdomains.
- A broken site is worse than an ad. If in doubt, do not add it.

---

## Commit messages

```
type(scope): imperative summary

Why this change, what it affects, and what a reviewer should check.
```

Types: `feat`, `fix`, `build`, `docs`, `refactor`, `perf`, `chore`, `release`.

---

## Reviewing agent-authored PRs

Trust but verify. An agent's summary describes intent, not outcome.

1. Read the diff, not the description.
2. Check that generated files were regenerated rather than hand-edited.
3. For flag or pref changes, ask for the `chrome://memory-internals` or `chrome://policy`
   evidence.
4. Confirm `docs/AGENT-STATE.md` was updated.
