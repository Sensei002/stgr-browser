# Contributing to STGR Browser

Thanks for helping build STGR Browser! This project is a thin, maintainable layer over the latest
stable Mozilla Firefox source. The most important rule:

> **Keep STGR modifications small, identifiable, and rebaseable.**
> Every change to upstream Firefox is a patch in `patches/` that must survive the next Firefox release.

## Code of conduct

Be respectful. This is an open-source project maintained by volunteers. Harassment, trolling, and
bad-faith contributions are not welcome.

## Ground rules

1. **Prefer configuration over code.** Many "features" (privacy defaults, telemetry toggles,
   performance tuning) are preference changes, not source changes. Put them in
   `stgr/config/preferences/` when possible.
2. **Small patches.** Each patch in `patches/` must have a header documenting:

   ```text
   Purpose:                why the patch exists
   Files changed:          upstream files touched
   Security impact:        does it change the security model? (it should not)
   Performance impact:     measured or estimated effect
   Upstream compatibility: rebase risk / known conflicts
   ```

3. **No bloat.** Every feature must answer (see §63 of the engineering spec):

   - Why does it exist?
   - What RAM does it use?
   - What CPU does it use?
   - Does it create network requests?
   - Does it increase attack surface?
   - Can it be optional?

   If you cannot answer these, the feature does not ship.

4. **Never weaken security.** No disabling of sandboxing, process isolation, certificate
   validation, or anti-exploitation mitigations — not even to win benchmarks.
5. **No telemetry.** STGR code must never collect browsing history, URLs, queries, fingerprints,
   usage statistics, or any user data. Ever.
6. **Test before you PR.** Run `python scripts/apply_patches.py check`, the Python linters, and any
   relevant unit tests (see `.github/workflows/tests.yml`).
7. **Don't break upstream attribution.** Preserve copyright notices and licenses for Firefox,
   uBlock Origin, and all third-party components.

## PR checklist

Every feature PR must explain:

- **Problem** — what user problem does this solve?
- **Solution** — what did you change, and where (config vs patch vs script)?
- **RAM impact** — expected memory delta.
- **CPU impact** — expected CPU delta.
- **Privacy impact** — any network or data behavior change?
- **Security impact** — does the security model change?
- **Firefox compatibility impact** — which upstream files change, and how hard will the next
  Firefox rebase hit?
- **Maintenance cost** — how much ongoing upkeep does this require?

Use the provided PR template if one is configured in your fork.

## Issue labels

Use these labels when triaging:

`bug` · `security` · `privacy` · `performance` · `memory` · `firefox-update` · `extension` ·
`uBlock` · `gaming-mode` · `ui` · `ci` · `build` · `installer` · `updater` · `documentation`

- `security` issues are private by default — report them via [`SECURITY.md`](SECURITY.md) first.
- `firefox-update` issues track Firefox Stable rebase work.

## Development workflow

```bash
# Sync Firefox source (first time / after update)
python scripts/update_firefox.py sync

# Apply / verify patches
python scripts/apply_patches.py apply
python scripts/apply_patches.py check

# Build (see docs/building.md)
python scripts/build_stgr.py build

# Lint your changes (Python)
python -m compileall -q scripts stgr
```

## Rebase policy

When Firefox updates and a patch conflicts:

1. **STOP.** Do not force the patch.
2. Run `python scripts/update_firefox.py` — it generates `firefox-update-report.md` listing failed
   patches and files needing manual review.
3. Fix the conflicts, verify the build, then merge.
4. Never release with unresolved patch conflicts.
